import React, { useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../context/AuthContext";
import api from "../../api/api";
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

  const fetchProfileData = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      if (!token) {
        navigate("/login");
        return;
      }

      const res = await api.get("/api/user/profile/");
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

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      setError("");

      const res = await api.put("/api/user/profile/update/", editData);

      if (res.data.success) {
        setProfileData(res.data.user);
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
              <button onClick={() => navigate("/")} className="btn btn-blue">
                Back to Home
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="btn btn-green"
              >
                Edit Profile
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="section">
              <h2 className="section-title">Edit Information</h2>

              <div className="form-group">
                <label className="form-label">Email:</label>
                <input
                  type="email"
                  name="email"
                  value={editData.email}
                  onChange={handleEditChange}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">First Name:</label>
                <input
                  type="text"
                  name="first_name"
                  value={editData.first_name}
                  onChange={handleEditChange}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Last Name:</label>
                <input
                  type="text"
                  name="last_name"
                  value={editData.last_name}
                  onChange={handleEditChange}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number:</label>
                <input
                  type="tel"
                  name="phone"
                  value={editData.phone}
                  onChange={handleEditChange}
                  className="form-input"
                />
              </div>
            </div>

            <div className="button-group">
              <button
                onClick={handleSaveProfile}
                disabled={isSaving}
                className={`btn btn-green ${isSaving ? "disabled" : ""}`}
              >
                {isSaving ? "Saving..." : "Save Changes"}
              </button>

              <button
                onClick={handleCancel}
                disabled={isSaving}
                className={`btn btn-gray ${isSaving ? "disabled" : ""}`}
              >
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Profile;
