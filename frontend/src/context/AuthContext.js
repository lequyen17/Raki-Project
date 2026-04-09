import React, { createContext, useState, useEffect } from 'react';
import api, { setAuthToken } from '../api/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkLoggedIn = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setCurrentUser(null);
        setLoading(false);
        return;
      }

      setAuthToken(token);
      try {
        const res = await api.get('/api/user/profile/');
        setCurrentUser(res.data);
      } catch (error) {
        localStorage.removeItem('access_token');
        setAuthToken(null);
        setCurrentUser(null);
      }
      setLoading(false);
    };
    checkLoggedIn();
  }, []);

  const logout = () => {
    localStorage.removeItem('access_token');
    setAuthToken(null);
    setCurrentUser(null);
    window.location.href = '/login';
  };

  const data = {
    currentUser,
    setCurrentUser,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={data}>
      {!loading && children}
    </AuthContext.Provider>
  );
};