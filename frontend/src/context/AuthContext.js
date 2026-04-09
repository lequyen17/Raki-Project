import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hàm kiểm tra User ngay khi load trang (F5 không bị mất login)
  useEffect(() => {
    const checkLoggedIn = async () => {
      const token = localStorage.getItem('access');
      if (token) {
        try {
          // Gọi API của Django để lấy thông tin user dựa trên token
          // Giả sử link là: /api/user/profile/
          const res = await axios.get('http://127.0.0.1:8000/api/user/profile/', {
            headers: { Authorization: `Bearer ${token}` }
          });
          setCurrentUser(res.data);
        } catch (error) {
          console.log("Token hết hạn hoặc lỗi:", error);
          localStorage.removeItem('access');
        }
      }
      setLoading(false);
    };
    checkLoggedIn();
  }, []);

  const logout = () => {
    localStorage.removeItem('access');
    setCurrentUser(null);
    window.location.href = '/login';
  };

  const data = {
    currentUser,
    setCurrentUser,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={data}>
      {!loading && children} 
    </AuthContext.Provider>
  );
};