import React, { useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthContext } from "../../context/AuthContext";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
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
  const [editData, setEditData] = useState({});
  const [formErrors, setFormErrors] = useState({});

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
        phone: res.data.phone,
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

  const handleSaveProfile = async () => {
    const errors = validateForm();

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      setIsSaving(true);
      setError("");

      const res = await api.put("/api/profile/", editData);

      if (res.data.success) {
        setProfileData(res.data.user);
        localStorage.setItem("user_data", JSON.stringify(res.data.user));
        setCurrentUser(res.data.user);
        setIsEditing(false);
      }
    } catch (err) {
      if (err.response?.data?.error) {
        setError(mapApiError(err.response.data.error, t, "profile.error_update"));
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
    setEditData({
      email: profileData.email,
      first_name: profileData.first_name,
      last_name: profileData.last_name,
      phone: profileData.phone,
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

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h1 className="profile-title">{t("profile.title")}</h1>

        {error && <div className="error-box">{error}</div>}

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
                disabled={isSaving}
                color="blue"
                size="lg"
              >
                {t("profile.save_changes")}
              </Button>

              <Button
                onClick={handleCancel}
                disabled={isSaving}
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
