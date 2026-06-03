import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// REQUEST: tự gắn token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// RESPONSE: refresh token flow
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Không chạy refresh token logic cho request login
    const isLoginRequest =
      originalRequest.url?.includes("/api/token/") &&
      !originalRequest.url?.includes("/api/token/refresh/");

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isLoginRequest
    ) {
      originalRequest._retry = true;

      const refresh = localStorage.getItem("refresh_token");

      if (!refresh) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(
          `${process.env.REACT_APP_API_URL}/api/token/refresh/`,
          { refresh },
        );

        const newAccess = res.data.access;
        const newRefresh = res.data.refresh;

        localStorage.setItem("access_token", newAccess);

        if (newRefresh) {
          localStorage.setItem("refresh_token", newRefresh);
        }

        // retry request (interceptor sẽ tự gắn token mới)
        return api(originalRequest);
      } catch (err) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
