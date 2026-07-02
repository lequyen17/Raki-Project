import axios from "axios";

const chatApi = axios.create({
  baseURL: "/api/chat",
  headers: {
    "Content-Type": "application/json",
  },
});

chatApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Dùng cho WebSocket khi access token hết hạn.
let refreshInFlight = null;
export async function refreshAccessToken() {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) {
      localStorage.clear();
      throw new Error("NO_REFRESH_TOKEN");
    }

    const res = await axios.post("/api/token/refresh/", { refresh });
    const newAccess = res.data.access;
    const newRefresh = res.data.refresh;

    if (newAccess) localStorage.setItem("access_token", newAccess);
    if (newRefresh) localStorage.setItem("refresh_token", newRefresh);

    return newAccess;
  })();

  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

chatApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const newAccess = await refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return chatApi(originalRequest);
      } catch (err) {
        localStorage.clear();
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  },
);

export const getChatWebSocketUrl = (conversationId) => {
  const token = localStorage.getItem("access_token");
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/api/chat/ws/${conversationId}?token=${token}`;
};

export default chatApi;
