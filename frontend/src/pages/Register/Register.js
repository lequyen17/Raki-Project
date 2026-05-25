import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Register.css";

const Register = () => {
  const { t } = useTranslation();
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
      newErrors.username = t("register.error_username_required");
    } else if (formData.username.trim().length < 3) {
      newErrors.username = t("register.error_username_min");
    } else if (formData.username.trim().length > 150) {
      newErrors.username = t("register.error_username_max");
    }

    if (!formData.email.trim()) {
      newErrors.email = t("register.error_email_required");
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      newErrors.email = t("register.error_email_invalid");
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = t("register.error_first_name_required");
    } else if (formData.first_name.trim().length < 2) {
      newErrors.first_name = t("register.error_first_name_min");
    } else if (formData.first_name.trim().length > 150) {
      newErrors.first_name = t("register.error_first_name_max");
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = t("register.error_last_name_required");
    } else if (formData.last_name.trim().length < 2) {
      newErrors.last_name = t("register.error_last_name_min");
    } else if (formData.last_name.trim().length > 150) {
      newErrors.last_name = t("register.error_last_name_max");
    }

    if (!formData.password) {
      newErrors.password = t("register.error_password_required");
    } else if (formData.password.length < 6) {
      newErrors.password = t("register.error_password_min");
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = t("register.error_confirm_required");
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = t("register.error_confirm_mismatch");
    }

    if (formData.phone && formData.phone.length > 15) {
      newErrors.phone = t("register.error_phone_invalid");
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

      navigate("/login");
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setGeneralError(mapApiError(err.response.data.error, t, "common.error_system"));
      } else {
        setGeneralError(t("common.error_system"));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-wrapper">
      <form onSubmit={handleSubmit} className="register-card">
        <h2 className="register-title">{t("register.title")}</h2>

        {success && (
          <div className="success">
            {t("register.success_message")}
          </div>
        )}
        {generalError && <div className="error">{generalError}</div>}

        <Input
          label={t("register.first_name_label")}
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          placeholder={t("register.first_name_placeholder")}
          required
          error={errors.first_name}
        />

        <Input
          label={t("register.last_name_label")}
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          placeholder={t("register.last_name_placeholder")}
          required
          error={errors.last_name}
        />

        <Input
          label={t("register.username_label")}
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder={t("register.username_placeholder")}
          required
          error={errors.username}
        />

        <Input
          label={t("register.email_label")}
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          placeholder={t("register.email_placeholder")}
          required
          error={errors.email}
        />

        <Input
          label={t("register.phone_label")}
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          placeholder={t("register.phone_placeholder")}
          error={errors.phone}
        />

        <Input
          label={t("register.password_label")}
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          placeholder={t("register.password_placeholder")}
          required
          error={errors.password}
        />

        <Input
          label={t("register.confirm_password_label")}
          name="confirm_password"
          type="password"
          value={formData.confirm_password}
          onChange={handleChange}
          placeholder={t("register.confirm_password_placeholder")}
          required
          error={errors.confirm_password}
        />

        <div
          style={{ display: "flex", justifyContent: "center", width: "100%" }}
        >
          <Button
            type="submit"
            color="blue"
            size="lg"
            isLoading={loading} // Truyền state loading vào đây
          >
            {t("register.submit")}
          </Button>
        </div>

        <div className="login-link">
          {t("register.already_have_account")}{" "}
          <Link to="/login" className="link">
            {t("register.login_here")}
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Register;
