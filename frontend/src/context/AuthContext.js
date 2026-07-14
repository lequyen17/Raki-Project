import React, { createContext, useState, useEffect, useCallback } from "react";
import { useLocation } from "react-router-dom";
import api from "../api/api";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const location = useLocation(); // Theo dõi route hiện tại

  // Hàm gọi API lấy thông tin User mới nhất
  const fetchUserData = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const response = await api.get("/api/auth/");
      const userData = response.data;

      // Cập nhật cả State và LocalStorage
      setCurrentUser(userData);
      localStorage.setItem("user_data", JSON.stringify(userData));
    } catch (error) {
      console.error("Lỗi khi đồng bộ user:", error);
      // Nếu token hết hạn hoặc lỗi nghiêm trọng, có thể logout ở đây
      if (error.response?.status === 401) logout();
    }
    console.log("đã set user data");
  }, []);

  useEffect(() => {
    const savedUser = localStorage.getItem("user_data");
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem("user_data");
      }
    }
    setLoading(false);
    fetchUserData(); // Fetch bản mới nhất ngay khi vào app
  }, [fetchUserData]);

  // 2. TỰ ĐỘNG GỌI KHI CHUYỂN ROUTE (Yêu cầu của bạn)
  // useEffect(() => {
  //   const token = localStorage.getItem("access_token");
  //   const publicPages = ["/", "/login", "/register"];
  //   const isPublicPage = publicPages.includes(location.pathname);

  //   if (token) {
  //     // 1. Nếu có token mà cố tình vào Login/Register -> Đẩy ra Dashboard
  //     if (isPublicPage) {
  //       navigate("/decks"); // Hoặc trang nào bạn muốn
  //     }

  //     // 2. Vẫn giữ logic fetch dữ liệu để đồng bộ
  //     fetchUserData();
  //   }
  // }, [location.pathname, fetchUserData, navigate]);

  const logout = () => {
    localStorage.clear();
    setCurrentUser(null);
    navigate("/login");
  };

  const value = {
    currentUser,
    setCurrentUser,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
