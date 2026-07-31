import api from "./api";

const NOTIFICATION_BASE_URL = "/api/notifications/";

export const notificationApi = {
  getNotifications: async () => {
    try {
      const response = await api.get(NOTIFICATION_BASE_URL);
      return response.data || [];
    } catch (error) {
      console.error("Failed to fetch notifications", error);
      return [];
    }
  },
};

export const getNotificationWebSocketUrl = () => {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const token = localStorage.getItem("access_token") || "";
  return `${protocol}//${window.location.host}/api/notifications/ws-notifications?token=${token}`;
};
