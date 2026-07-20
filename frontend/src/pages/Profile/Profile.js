import React, { useContext, useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthContext } from "../../context/AuthContext";
import api from "../../api/api";
import { getApiErrorCode, mapApiError } from "../../utils/errorMapper";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Profile.css";

const Profile = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { currentUser, logout, setCurrentUser } = useContext(AuthContext);
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [editData, setEditData] = useState({});
  const [formErrors, setFormErrors] = useState({});
  const avatarInputRef = useRef(null);

  const syncLocalUser = useCallback(
    (user) => {
      localStorage.setItem("user_data", JSON.stringify(user));
      setCurrentUser((prev) => ({
        ...(prev || {}),
        id: user.id,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
        avatar: user.avatar,
      }));
    },
    [setCurrentUser],
  );

  const applyAvatarUrl = useCallback(
    (avatarUrl) => {
      setProfileData((prev) => (prev ? { ...prev, avatar: avatarUrl } : prev));
      setEditData((prev) => ({ ...prev, avatar: avatarUrl }));
      setCurrentUser((prev) => (prev ? { ...prev, avatar: avatarUrl } : prev));
      const saved = localStorage.getItem("user_data");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          localStorage.setItem(
            "user_data",
            JSON.stringify({ ...parsed, avatar: avatarUrl }),
          );
        } catch (_) {
          /* ignore */
        }
      }
    },
    [setCurrentUser],
  );

  const fetchProfileData = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      if (!token) {
        navigate("/login");
        return;
      }

      const res = await api.get("/api/profile/");
      setProfileData(res.data);
      setEditData({
        email: res.data.email,
        first_name: res.data.first_name,
        last_name: res.data.last_name,
        phone: res.data.phone || "",
        avatar: res.data.avatar || "",
      });
      setError("");
    } catch (err) {
      console.error("Error fetching profile:", err);
      setError(t("profile.error_load"));
      if (err.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [navigate, logout, t]);

  useEffect(() => {
    if (!currentUser) {
      navigate("/login");
      return;
    }
    fetchProfileData();
  }, [currentUser, navigate, fetchProfileData]);

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    const errors = {};

    if (!editData.email.trim()) {
      errors.email = t("profile.error_email_required");
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editData.email)) {
      errors.email = t("profile.error_email_invalid");
    }

    if (editData.first_name && editData.first_name.length < 2) {
      errors.first_name = t("profile.error_first_name_min");
    }

    if (editData.phone && editData.phone.length > 15) {
      errors.phone = t("profile.error_phone_invalid");
    }

    return errors;
  };

  const handleAvatarEditClick = (e) => {
    e.stopPropagation();
    if (isUploadingAvatar) return;
    avatarInputRef.current?.click();
  };

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError(t("profile.error_avatar_type"));
      return;
    }

    try {
      setIsUploadingAvatar(true);
      setError("");

      const formData = new FormData();
      formData.append("avatar", file);

      const res = await api.post("/api/profile/avatar/", formData, {
        transformRequest: [
          (data, headers) => {
            if (headers && typeof headers.delete === "function") {
              headers.delete("Content-Type");
            } else if (headers) {
              delete headers["Content-Type"];
            }
            return data;
          },
        ],
      });

      const avatarUrl = res.data?.avatar;
      if (!avatarUrl) {
        setError(t("profile.error_avatar_upload"));
        return;
      }

      applyAvatarUrl(avatarUrl);
    } catch (err) {
      const errorCode = getApiErrorCode(err.response?.data);
      if (errorCode) {
        setError(mapApiError(errorCode, t, "profile.error_avatar_upload"));
      } else {
        setError(t("profile.error_avatar_upload"));
      }
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handleSaveProfile = async () => {
    const errors = validateForm();

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      setIsSaving(true);
      setError("");

      // Chỉ cập nhật thông tin text — avatar đổi riêng qua POST /api/profile/avatar/
      const res = await api.put("/api/profile/", {
        email: editData.email,
        first_name: editData.first_name,
        last_name: editData.last_name,
        phone: editData.phone,
      });

      if (res.data.success) {
        setProfileData(res.data.user);
        setEditData({
          email: res.data.user.email,
          first_name: res.data.user.first_name,
          last_name: res.data.user.last_name,
          phone: res.data.user.phone || "",
          avatar: res.data.user.avatar || "",
        });
        syncLocalUser(res.data.user);
        setIsEditing(false);
      }
    } catch (err) {
      const errorCode = getApiErrorCode(err.response?.data);
      if (errorCode) {
        setError(mapApiError(errorCode, t, "profile.error_update"));
      } else {
        setError(t("profile.error_update"));
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setError("");
    setFormErrors({});
    setEditData({
      email: profileData.email,
      first_name: profileData.first_name,
      last_name: profileData.last_name,
      phone: profileData.phone || "",
      avatar: profileData.avatar || "",
    });
  };

  if (loading) {
    return (
      <div className="profile-container">
        <p>{t("common.loading")}</p>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="profile-container">
        <p>{t("profile.not_found")}</p>
      </div>
    );
  }

  const displayAvatar = profileData.avatar;
  const avatarInitial =
    (profileData.first_name || profileData.username || "?").charAt(0).toUpperCase();

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h1 className="profile-title">{t("profile.title")}</h1>

        {error && <div className="error-box">{error}</div>}

        <div className="profile-avatar-section">
          <div
            className={`profile-avatar-wrap${isUploadingAvatar ? " profile-avatar-wrap--loading" : ""}`}
          >
            <div className="profile-avatar-frame" aria-hidden={false}>
              {displayAvatar ? (
                <img
                  src={displayAvatar}
                  alt={profileData.username}
                  className="profile-avatar-frame__image"
                />
              ) : (
                <span className="profile-avatar-frame__fallback">
                  {avatarInitial}
                </span>
              )}
              {isUploadingAvatar && (
                <span className="profile-avatar-frame__loading">
                  {t("common.loading")}
                </span>
              )}
            </div>
            <button
              type="button"
              className="profile-avatar-edit-btn"
              onClick={handleAvatarEditClick}
              disabled={isUploadingAvatar}
              aria-label={t("profile.change_avatar")}
              title={t("profile.change_avatar")}
            >
              <svg
                viewBox="0 0 24 24"
                width="14"
                height="14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
              </svg>
            </button>
          </div>
          <input
            ref={avatarInputRef}
            type="file"
            accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
            className="profile-avatar-input"
            onChange={handleAvatarChange}
          />
        </div>

        {!isEditing ? (
          <>
            <div className="section">
              <h2 className="section-title">{t("profile.personal_info")}</h2>
              <div className="info-grid">
                <div className="info-row">
                  <span className="label">{t("profile.username_label")}</span>
                  <span className="value">{profileData.username}</span>
                </div>
                <div className="info-row">
                  <span className="label">{t("profile.email_label")}</span>
                  <span className="value">{profileData.email}</span>
                </div>
                <div className="info-row">
                  <span className="label">{t("profile.first_name_label")}</span>
                  <span className="value">
                    {profileData.first_name || t("common.not_updated")}
                  </span>
                </div>
                <div className="info-row">
                  <span className="label">{t("profile.last_name_label")}</span>
                  <span className="value">
                    {profileData.last_name || t("common.not_updated")}
                  </span>
                </div>
                <div className="info-row">
                  <span className="label">{t("profile.phone_label")}</span>
                  <span className="value">
                    {profileData.phone || t("common.not_updated")}
                  </span>
                </div>
              </div>
            </div>

            <div className="section">
              <h2 className="section-title">{t("profile.learning_stats")}</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">{profileData.total_cards}</div>
                  <div className="stat-label">{t("profile.total_cards")}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">
                    {profileData.total_learned_cards}
                  </div>
                  <div className="stat-label">{t("profile.learned_cards")}</div>
                </div>
              </div>
            </div>

            <div className="button-group">
              <Button onClick={() => navigate("/decks")} color="blue" size="lg">
                {t("profile.back_to_home")}
              </Button>
              <Button
                onClick={() => setIsEditing(true)}
                color="green"
                size="lg"
              >
                {t("profile.edit_profile")}
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className="section">
              <h2 className="section-title">{t("profile.edit_info")}</h2>

              <Input
                label={t("profile.email_label")}
                name="email"
                type="email"
                value={editData.email}
                onChange={handleEditChange}
                error={formErrors.email}
              />

              <Input
                label={t("profile.first_name_label")}
                name="first_name"
                value={editData.first_name}
                onChange={handleEditChange}
                error={formErrors.first_name}
              />

              <Input
                label={t("profile.last_name_label")}
                name="last_name"
                value={editData.last_name}
                onChange={handleEditChange}
                error={formErrors.last_name}
              />

              <Input
                label={t("profile.phone_label")}
                name="phone"
                type="tel"
                value={editData.phone}
                onChange={handleEditChange}
                error={formErrors.phone}
              />
            </div>

            <div className="button-group">
              <Button
                onClick={handleSaveProfile}
                disabled={isSaving || isUploadingAvatar}
                color="blue"
                size="lg"
              >
                {t("profile.save_changes")}
              </Button>

              <Button
                onClick={handleCancel}
                disabled={isSaving || isUploadingAvatar}
                size="lg"
                color="green"
              >
                {t("profile.cancel")}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Profile;
