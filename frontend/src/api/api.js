import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",

  // baseURL: "http://192.168.10.40:8000",
  // baseURL: process.env.REACT_APP_API_URL || "http://127.0.0.1:8000",
});

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
};

export default api;
