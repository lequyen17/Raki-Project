import React, { createContext, useState, useEffect } from 'react';
import api, { setAuthToken } from '../api/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Không cần khai báo hàm checkLoggedIn async phức tạp nữa
    // vì ta đọc từ LocalStorage là đồng bộ (synchronous)
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user_data');

    if (token && savedUser) {
      setAuthToken(token);
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (e) {
        // Phòng trường hợp user_data trong máy bị lỗi format JSON
        localStorage.removeItem('user_data');
      }
    }
    setLoading(false);
  }, []);

  const logout = () => {
    localStorage.clear(); // Xóa sạch sành sanh cho nhanh
    setAuthToken(null);
    setCurrentUser(null);
    window.location.href = '/login';
  };

  // Sử dụng shorthand property (currentUser: currentUser -> currentUser)
  const value = { currentUser, setCurrentUser, logout, loading };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};