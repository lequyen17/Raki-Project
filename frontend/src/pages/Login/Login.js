import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../api/api";
import { AuthContext } from "../../context/AuthContext";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import "./Login.css"; // CSS đã được import ở đây

const Login = () => {
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
    setError(""); // Reset lỗi mỗi lần bấm submit

    try {
      const res = await api.post("/api/login/", formData);
      const { access, refresh, user } = res.data;

      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);
      localStorage.setItem("user_data", JSON.stringify(user));

      setCurrentUser(user);

      navigate("/decks");
    } catch (err) {
      if (
        err.response &&
        (err.response.status === 400 || err.response.status === 401)
      ) {
        setError("Invalid username or password.");
      } else {
        setError("System error. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrapper">
      <form onSubmit={handleSubmit} className="login-card">
        <h2 className="login-title">Login</h2>

        {error && <div className="login-error">{error}</div>}

        <Input
          label="Username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          required
          placeholder="Enter your username"
        />

        <Input
          label="Password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          required
          placeholder="Enter your password"
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
            Sign In
          </Button>
        </div>
      </form>
    </div>
  );
};

export default Login;
