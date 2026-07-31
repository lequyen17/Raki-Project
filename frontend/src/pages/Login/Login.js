import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { AuthContext } from "../../context/AuthContext";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Login.css"; // CSS đã được import ở đây

const Login = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setCurrentUser } = useContext(AuthContext);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Đăng nhập
      const loginRes = await api.post("/api/token/", formData);
      const { access, refresh } = loginRes.data;

      // Lưu token
      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);

      // Lấy thông tin user
      const userRes = await api.get("/api/auth/");
      const user = userRes.data;

      // Cập nhật Context và LocalStorage
      setCurrentUser(user);
      localStorage.setItem("user_data", JSON.stringify(user));

      navigate("/decks");
    } catch (err) {
      if (
        err.response &&
        (err.response.status === 400 || err.response.status === 401)
      ) {
        setError(t("login.error_invalid"));
      } else {
        setError(t("common.error_system"));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrapper">
      <form onSubmit={handleSubmit} className="login-card">
        <h2 className="login-title">{t("login.title")}</h2>

        {error && <div className="login-error">{error}</div>}

        <Input
          label={t("login.username_label")}
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          required
          placeholder={t("login.username_placeholder")}
        />

        <Input
          label={t("login.password_label")}
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          required
          placeholder={t("login.password_placeholder")}
        />

        <div
          style={{ display: "flex", justifyContent: "center", width: "100%" }}
        >
          <Button
            type="submit"
            color="blue"
            size="lg" // Kích thước trung bình
            isLoading={loading} // Truyền state loading vào đây
          >
            {t("login.submit")}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default Login;
