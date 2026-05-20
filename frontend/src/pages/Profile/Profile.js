import React, { useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import api from "../../api/api";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Profile.css";

const Profile = () => {
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
      setError("Cannot load profile data");
      if (err.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [navigate, logout]);

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
      errors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editData.email)) {
      errors.email = "Invalid email";
    }

    if (editData.first_name && editData.first_name.length < 2) {
      errors.first_name = "First name must be at least 2 chars";
    }

    if (editData.phone && editData.phone.length > 15) {
      errors.phone = "Invalid phone";
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
        setError(err.response.data.error);
      } else {
        setError("Cannot update profile");
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
        <p>Loading...</p>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="profile-container">
        <p>Profile data not found</p>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h1 className="profile-title">My Profile</h1>

        {error && <div className="error-box">{error}</div>}

        {!isEditing ? (
          <>
            <div className="section">
              <h2 className="section-title">Personal Information</h2>
              <div className="info-grid">
                <div className="info-row">
                  <span className="label">Username:</span>
                  <span className="value">{profileData.username}</span>
                </div>
                <div className="info-row">
                  <span className="label">Email:</span>
                  <span className="value">{profileData.email}</span>
                </div>
                <div className="info-row">
                  <span className="label">First Name:</span>
                  <span className="value">
                    {profileData.first_name || "Not updated yet"}
                  </span>
                </div>
                <div className="info-row">
                  <span className="label">Last Name:</span>
                  <span className="value">
                    {profileData.last_name || "Not updated yet"}
                  </span>
                </div>
                <div className="info-row">
                  <span className="label">Phone Number:</span>
                  <span className="value">
                    {profileData.phone || "Not updated yet"}
                  </span>
                </div>
              </div>
            </div>

            <div className="section">
              <h2 className="section-title">Learning Statistics</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">{profileData.total_cards}</div>
                  <div className="stat-label">Total Cards</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">
                    {profileData.total_learned_cards}
                  </div>
                  <div className="stat-label">Learned Cards</div>
                </div>
              </div>
            </div>

            <div className="button-group">
              <Button onClick={() => navigate("/decks")} color="blue" size="lg">
                Back to Home
              </Button>
              <Button
                onClick={() => setIsEditing(true)}
                color="green"
                size="lg"
              >
                Edit Profile
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className="section">
              <h2 className="section-title">Edit Information</h2>

              <Input
                label="Email"
                name="email"
                type="email"
                value={editData.email}
                onChange={handleEditChange}
                error={formErrors.email}
              />

              <Input
                label="First Name"
                name="first_name"
                value={editData.first_name}
                onChange={handleEditChange}
                error={formErrors.first_name}
              />

              <Input
                label="Last Name"
                name="last_name"
                value={editData.last_name}
                onChange={handleEditChange}
                error={formErrors.last_name}
              />

              <Input
                label="Phone Number"
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
                Save Changes
              </Button>

              <Button
                onClick={handleCancel}
                disabled={isSaving}
                size="lg"
                color="green"
              >
                Cancel
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Profile;
