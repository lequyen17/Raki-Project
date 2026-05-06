import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../../api/api";
import "./Register.css";

const Register = () => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirm_password: "",
    email: "",
    first_name: "",
    last_name: "",
    phone: "",
  });
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
    setGeneralError("");
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = "Username is required";
    } else if (formData.username.trim().length < 3) {
      newErrors.username = "Username must be at least 3 characters";
    } else if (formData.username.trim().length > 150) {
      newErrors.username = "Username must be 150 characters or less";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      newErrors.email = "Invalid email address";
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = "First name is required";
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = "First name must be at least 2 characters";
    } else if (formData.first_name.trim().length > 150) {
      newErrors.first_name = "First name must be 150 characters or less";
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = "Last name is required";
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = "Last name must be at least 2 characters";
    } else if (formData.last_name.trim().length > 150) {
      newErrors.last_name = "Last name must be 150 characters or less";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = "Please confirm your password";
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = "Password confirmation does not match";
    }

    if (formData.phone && formData.phone.length > 15) {
      newErrors.phone = "Invalid phone number";
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError("");
    setSuccess(false);

    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);

    try {
      await api.post("/api/register/", {
        username: formData.username.trim(),
        password: formData.password,
        confirm_password: formData.confirm_password,
        email: formData.email.trim(),
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        phone: formData.phone.trim(),
      });

      setSuccess(true);
      setFormData({
        username: "",
        password: "",
        confirm_password: "",
        email: "",
        first_name: "",
        last_name: "",
        phone: "",
      });
      setErrors({});

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setGeneralError(err.response.data.error);
      } else {
        setGeneralError("System error. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-wrapper">
      <form onSubmit={handleSubmit} className="register-card">
        <h2 className="register-title">Create Account</h2>

        {success && (
          <div className="success">
            Registration successful! Redirecting to login...
          </div>
        )}
        {generalError && <div className="error">{generalError}</div>}

        <div className="input-group">
          <label>First Name *</label>
          <input
            name="first_name"
            type="text"
            className={`input ${errors.first_name ? "input-error" : ""}`}
            value={formData.first_name}
            onChange={handleChange}
            placeholder="Enter first name"
          />
          {errors.first_name && (
            <span className="error-text">{errors.first_name}</span>
          )}
        </div>

        <div className="input-group">
          <label>Last Name *</label>
          <input
            name="last_name"
            type="text"
            className={`input ${errors.last_name ? "input-error" : ""}`}
            value={formData.last_name}
            onChange={handleChange}
            placeholder="Enter last name"
          />
          {errors.last_name && (
            <span className="error-text">{errors.last_name}</span>
          )}
        </div>

        <div className="input-group">
          <label>Username *</label>
          <input
            name="username"
            type="text"
            className={`input ${errors.username ? "input-error" : ""}`}
            value={formData.username}
            onChange={handleChange}
            placeholder="Enter username"
          />
          {errors.username && (
            <span className="error-text">{errors.username}</span>
          )}
        </div>

        <div className="input-group">
          <label>Email *</label>
          <input
            name="email"
            type="email"
            className={`input ${errors.email ? "input-error" : ""}`}
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter email"
          />
          {errors.email && <span className="error-text">{errors.email}</span>}
        </div>

        <div className="input-group">
          <label>Phone Number</label>
          <input
            name="phone"
            type="tel"
            className={`input ${errors.phone ? "input-error" : ""}`}
            value={formData.phone}
            onChange={handleChange}
            placeholder="Enter phone (optional)"
          />
          {errors.phone && <span className="error-text">{errors.phone}</span>}
        </div>

        <div className="input-group">
          <label>Password *</label>
          <input
            name="password"
            type="password"
            className={`input ${errors.password ? "input-error" : ""}`}
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter password"
          />
          {errors.password && (
            <span className="error-text">{errors.password}</span>
          )}
        </div>

        <div className="input-group">
          <label>Confirm Password *</label>
          <input
            name="confirm_password"
            type="password"
            className={`input ${errors.confirm_password ? "input-error" : ""}`}
            value={formData.confirm_password}
            onChange={handleChange}
            placeholder="Confirm password"
          />
          {errors.confirm_password && (
            <span className="error-text">{errors.confirm_password}</span>
          )}
        </div>

        <button type="submit" className="register-button" disabled={loading}>
          {loading ? "Please wait..." : "Register"}
        </button>

        <div className="login-link">
          Already have an account?{" "}
          <Link to="/login" className="link">
            Login here
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Register;
