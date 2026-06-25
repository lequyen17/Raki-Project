import axios from "axios";

const api = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

// Các biến phục vụ việc xếp hàng (Queue) chống race-condition
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// REQUEST INTERCEPTOR
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// RESPONSE INTERCEPTOR
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Loại bỏ tất cả các request auth để tránh lặp vô hạn
    const isAuthRequest =
      originalRequest.url?.includes("/api/token/") ||
      originalRequest.url?.includes("/api/token/refresh/");

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isAuthRequest
    ) {
      // Nếu đang có một request khác đi đổi token rồi, thì request này đứng đợi
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      // Đánh dấu bắt đầu quá trình đổi token
      originalRequest._retry = true;
      isRefreshing = true;

      const refresh = localStorage.getItem("refresh_token");

      if (!refresh) {
        localStorage.clear();
        window.location.href = "/";
        return Promise.reject(error);
      }

      try {
        const res = await axios.post("/api/token/refresh/", { refresh });

        const newAccess = res.data.access;
        const newRefresh = res.data.refresh;

        localStorage.setItem("access_token", newAccess);
        if (newRefresh) {
          localStorage.setItem("refresh_token", newRefresh);
        }

        // Giải phóng hàng đợi, cho phép các request sau chạy tiếp với token mới
        processQueue(null, newAccess);

        // Thực hiện lại request hiện tại
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch (err) {
        // Nếu đổi token thất bại (RT hết hạn thực sự), hủy hàng đợi và logout
        processQueue(err, null);
        localStorage.clear();
        window.location.href = "/";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default api;
