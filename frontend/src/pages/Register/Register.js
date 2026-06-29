import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Register.css";

const OTP_LENGTH = 6;
const OTP_TTL = 300; // 5 phút (giây)
const RESEND_COOLDOWN = 60; // giây

const Register = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  // ── Step state ─────────────────────────────────────────
  const [step, setStep] = useState("form"); // "form" | "otp"

  // ── Form state ─────────────────────────────────────────
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

  // ── OTP state ──────────────────────────────────────────
  const [otpDigits, setOtpDigits] = useState(Array(OTP_LENGTH).fill(""));
  const [otpError, setOtpError] = useState("");
  const [otpLoading, setOtpLoading] = useState(false);
  const [countdown, setCountdown] = useState(OTP_TTL);
  const [resendCooldown, setResendCooldown] = useState(0);
  const inputRefs = useRef([]);
  const countdownRef = useRef(null);
  const resendRef = useRef(null);

  // ── Countdown timer ────────────────────────────────────
  const startCountdown = useCallback(() => {
    clearInterval(countdownRef.current);
    setCountdown(OTP_TTL);
    countdownRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(countdownRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  const startResendCooldown = useCallback(() => {
    clearInterval(resendRef.current);
    setResendCooldown(RESEND_COOLDOWN);
    resendRef.current = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(resendRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  useEffect(() => {
    return () => {
      clearInterval(countdownRef.current);
      clearInterval(resendRef.current);
    };
  }, []);

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60)
      .toString()
      .padStart(2, "0");
    const s = (secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  // ── Form helpers ───────────────────────────────────────
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (errors[name]) setErrors({ ...errors, [name]: "" });
    setGeneralError("");
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.username.trim())
      newErrors.username = t("register.error_username_required");
    else if (formData.username.trim().length < 3)
      newErrors.username = t("register.error_username_min");
    else if (formData.username.trim().length > 150)
      newErrors.username = t("register.error_username_max");

    if (!formData.email.trim())
      newErrors.email = t("register.error_email_required");
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim()))
      newErrors.email = t("register.error_email_invalid");

    if (!formData.first_name.trim())
      newErrors.first_name = t("register.error_first_name_required");
    else if (formData.first_name.trim().length < 2)
      newErrors.first_name = t("register.error_first_name_min");
    else if (formData.first_name.trim().length > 150)
      newErrors.first_name = t("register.error_first_name_max");

    if (!formData.last_name.trim())
      newErrors.last_name = t("register.error_last_name_required");
    else if (formData.last_name.trim().length < 2)
      newErrors.last_name = t("register.error_last_name_min");
    else if (formData.last_name.trim().length > 150)
      newErrors.last_name = t("register.error_last_name_max");

    if (!formData.password)
      newErrors.password = t("register.error_password_required");
    else if (formData.password.length < 6)
      newErrors.password = t("register.error_password_min");

    if (!formData.confirm_password)
      newErrors.confirm_password = t("register.error_confirm_required");
    else if (formData.password !== formData.confirm_password)
      newErrors.confirm_password = t("register.error_confirm_mismatch");

    if (formData.phone && formData.phone.length > 15)
      newErrors.phone = t("register.error_phone_invalid");

    return newErrors;
  };

  // ── Step 1: Send OTP ───────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError("");

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

      setStep("otp");
      setOtpDigits(Array(OTP_LENGTH).fill(""));
      setOtpError("");
      startCountdown();
      startResendCooldown();
      // focus đầu tiên sau khi render
      setTimeout(() => inputRefs.current[0]?.focus(), 50);
    } catch (err) {
      if (err.response?.data?.error) {
        setGeneralError(
          mapApiError(err.response.data.error, t, "common.error_system")
        );
      } else {
        setGeneralError(t("common.error_system"));
      }
    } finally {
      setLoading(false);
    }
  };

  // ── OTP input handlers ─────────────────────────────────
  const handleOtpChange = (index, value) => {
    if (!/^\d*$/.test(value)) return; // chỉ số
    const updated = [...otpDigits];
    updated[index] = value.slice(-1); // 1 ký tự
    setOtpDigits(updated);
    setOtpError("");
    if (value && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === "Backspace" && !otpDigits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === "ArrowLeft" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === "ArrowRight" && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text").replace(/\D/g, "");
    if (!text) return;
    const updated = Array(OTP_LENGTH).fill("");
    for (let i = 0; i < OTP_LENGTH && i < text.length; i++) {
      updated[i] = text[i];
    }
    setOtpDigits(updated);
    const nextFocus = Math.min(text.length, OTP_LENGTH - 1);
    inputRefs.current[nextFocus]?.focus();
  };

  // ── Step 2: Verify OTP ─────────────────────────────────
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    const otp = otpDigits.join("");
    if (otp.length < OTP_LENGTH) {
      setOtpError(t("register.otp_label") + " " + t("register.error_username_required").replace("Username", "OTP"));
      return;
    }
    if (countdown === 0) {
      setOtpError(t("register.otp_expired_message"));
      return;
    }

    setOtpLoading(true);
    setOtpError("");
    try {
      await api.post("/api/register/verify-otp/", {
        email: formData.email.trim(),
        otp,
      });
      // Thành công → redirect login
      navigate("/login");
    } catch (err) {
      if (err.response?.data?.error) {
        setOtpError(
          mapApiError(err.response.data.error, t, "common.error_system")
        );
      } else {
        setOtpError(t("common.error_system"));
      }
    } finally {
      setOtpLoading(false);
    }
  };

  // ── Resend OTP ─────────────────────────────────────────
  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setOtpError("");
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
      setOtpDigits(Array(OTP_LENGTH).fill(""));
      startCountdown();
      startResendCooldown();
      setTimeout(() => inputRefs.current[0]?.focus(), 50);
    } catch (err) {
      setOtpError(t("common.error_system"));
    } finally {
      setLoading(false);
    }
  };

  // ── Render: Form ───────────────────────────────────────
  if (step === "form") {
    return (
      <div className="register-wrapper">
        <form onSubmit={handleSubmit} className="register-card">
          <h2 className="register-title">{t("register.title")}</h2>

          {generalError && <div className="reg-error">{generalError}</div>}

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

          <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
            <Button type="submit" color="blue" size="lg" isLoading={loading}>
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
  }

  // ── Render: OTP screen ─────────────────────────────────
  return (
    <div className="register-wrapper">
      <form onSubmit={handleVerifyOtp} className="register-card otp-card">
        {/* Icon */}
        <div className="otp-icon-wrap">
          <div className="otp-icon">✉️</div>
        </div>

        <h2 className="register-title">{t("register.otp_title")}</h2>
        <p className="otp-subtitle">
          {t("register.otp_subtitle")}{" "}
          <strong className="otp-email">{formData.email}</strong>
        </p>

        {/* Countdown */}
        <div className={`otp-countdown ${countdown === 0 ? "expired" : ""}`}>
          {countdown > 0 ? (
            <>
              <span className="otp-expires-label">{t("register.otp_expires_in")}</span>
              <span className="otp-timer">{formatTime(countdown)}</span>
            </>
          ) : (
            <span className="otp-expired-text">
              {t("register.otp_expired_message")}
            </span>
          )}
        </div>

        {/* 6 OTP boxes */}
        <div className="otp-inputs" onPaste={handleOtpPaste}>
          {otpDigits.map((digit, i) => (
            <input
              key={i}
              id={`otp-input-${i}`}
              ref={(el) => (inputRefs.current[i] = el)}
              className={`otp-box ${digit ? "otp-box--filled" : ""} ${otpError ? "otp-box--error" : ""}`}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleOtpChange(i, e.target.value)}
              onKeyDown={(e) => handleOtpKeyDown(i, e)}
              autoComplete="one-time-code"
            />
          ))}
        </div>

        {otpError && <div className="reg-error otp-error-msg">{otpError}</div>}

        {/* Verify button */}
        <div style={{ display: "flex", justifyContent: "center", width: "100%", marginTop: "8px" }}>
          <Button
            type="submit"
            color="blue"
            size="lg"
            isLoading={otpLoading}
            disabled={countdown === 0}
          >
            {t("register.otp_submit")}
          </Button>
        </div>

        {/* Resend */}
        <div className="otp-resend-wrap">
          {resendCooldown > 0 ? (
            <span className="otp-resend-hint">
              {t("register.otp_resend_in", { seconds: resendCooldown })}
            </span>
          ) : (
            <button
              type="button"
              className="otp-resend-btn"
              onClick={handleResend}
              disabled={loading}
            >
              {loading ? "..." : t("register.otp_resend")}
            </button>
          )}
        </div>

        {/* Back */}
        <div className="login-link">
          <button
            type="button"
            className="otp-back-btn"
            onClick={() => {
              clearInterval(countdownRef.current);
              clearInterval(resendRef.current);
              setStep("form");
              setOtpError("");
            }}
          >
            {t("register.otp_back")}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Register;
