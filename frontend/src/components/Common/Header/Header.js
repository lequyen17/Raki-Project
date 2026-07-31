import React, { useState, useContext, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthContext } from "../../../context/AuthContext.js";
import {
  notificationApi,
  getNotificationWebSocketUrl,
} from "../../../api/notificationApi.js";
import "./Header.css";

const Header = () => {
  const { t } = useTranslation();
  const { currentUser, logout } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);
  const [notiOpen, setNotiOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const menuRef = useRef(null);
  const notiRef = useRef(null);
  const stompClientRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
      if (notiRef.current && !notiRef.current.contains(event.target)) {
        setNotiOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [currentUser?.id]);

  // Fetch initial notifications
  useEffect(() => {
    if (currentUser && currentUser.id) {
      notificationApi.getNotifications().then((data) => {
        setNotifications(data);
        setUnreadCount(data.filter((n) => !n.isRead).length);
      });
    }
  }, [currentUser?.id]);

  // WebSocket Connection for Notifications
  useEffect(() => {
    if (!currentUser || !currentUser.id) return;

    let ws = null;
    const connectWebSocket = () => {
      ws = new WebSocket(getNotificationWebSocketUrl());

      ws.onopen = () => {
        console.log("Connected to native notification websocket");
      };

      ws.onmessage = (event) => {
        try {
          const newNoti = JSON.parse(event.data);
          setNotifications((prev) => [newNoti, ...prev]);
          setUnreadCount((prev) => prev + 1);
        } catch (e) {
          console.error("Error parsing notification message", e);
        }
      };

      ws.onerror = (error) => {
        console.error("Notification WebSocket error", error);
      };

      ws.onclose = () => {
        console.log("Notification WebSocket disconnected. Retrying in 5s...");
        setTimeout(connectWebSocket, 5000); // Reconnect
      };

      stompClientRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (stompClientRef.current) {
        stompClientRef.current.onclose = null; // Prevent reconnect loop on unmount
        stompClientRef.current.close();
      }
    };
  }, [currentUser?.id]);

  const handleProfileClick = () => {
    setMenuOpen(false);
    navigate("/profile");
  };
  const handleSettingClick = () => {
    setMenuOpen(false);
    navigate("/settings");
  };
  const handleWalletClick = () => {
    setMenuOpen(false);
    navigate("/wallet");
  };
  const handleDecksClick = () => {
    setMenuOpen(false);
    navigate("/decks");
  };

  const handleToggleMenu = () => {
    setMenuOpen((open) => !open);
    setNotiOpen(false);
  };

  const handleToggleNoti = () => {
    setNotiOpen((open) => !open);
    setMenuOpen(false);
    if (!notiOpen && unreadCount > 0) {
      // In a real app, you might want to call an API to mark as read here
      setUnreadCount(0);
    }
  };

  return (
    <header className="raki-header">
      <div className="container raki-header__inner">
        {/* LEFT SIDE */}
        <div
          className="raki-left"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "24px",
          }}
        >
          <div className="raki-brand">
            {currentUser ? (
              <Link to="/decks" className="raki-logo">
                <span className="raki-logo__text">
                  <span className="raki-logo__accent">ra</span>ki
                </span>
              </Link>
            ) : (
              <a href="/" className="raki-logo">
                <span className="raki-logo__text">
                  <span className="raki-logo__accent">ra</span>ki
                </span>
              </a>
            )}
          </div>

          <nav className="raki-nav-links">
            <Link to="/decks" className="raki-nav-item">
              {t("header.MY_DECKS")}
            </Link>

            <Link to="/community" className="raki-nav-item">
              {t("header.COMMUNITY")}
            </Link>

            <Link to="/chat" className="raki-nav-item">
              {t("header.CHAT")}
            </Link>
          </nav>
        </div>

        <div className="raki-actions">
          {!currentUser ? (
            <div className="raki-auth">
              <Link
                to="/register"
                className="raki-button raki-button--secondary"
              >
                {t("header.register")}
              </Link>
              <Link to="/login" className="raki-button raki-button--primary">
                {t("header.login")}
              </Link>
            </div>
          ) : (
            <div
              className="raki-actions-logged-in"
              style={{ display: "flex", alignItems: "center", gap: "16px" }}
            >
              {/* Notification Bell */}
              <div className="raki-noti" ref={notiRef}>
                <button
                  type="button"
                  className={`raki-noti__toggle${notiOpen ? " raki-noti__toggle--open" : ""}`}
                  onClick={handleToggleNoti}
                  aria-expanded={notiOpen}
                  aria-haspopup="menu"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                    <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
                  </svg>
                  {unreadCount > 0 && (
                    <span className="raki-noti__badge">
                      {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                  )}
                </button>

                {notiOpen && (
                  <div className="raki-noti__menu" role="menu">
                    <div className="raki-noti__header">
                      <h3>{t("header.notifications", "Notifications")}</h3>
                    </div>
                    <div className="raki-noti__list">
                      {notifications.length === 0 ? (
                        <div className="raki-noti__empty">
                          {t(
                            "header.no_notifications",
                            "No notifications yet.",
                          )}
                        </div>
                      ) : (
                        notifications.map((noti, idx) => (
                          <div
                            key={noti.id || idx}
                            className={`raki-noti__item ${!noti.isRead ? "raki-noti__item--unread" : ""}`}
                          >
                            <div className="raki-noti__content">
                              <strong>{noti.title}</strong>
                              <p>{noti.content}</p>
                              <span className="raki-noti__time">
                                {new Date(noti.createdAt).toLocaleString()}
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Profile Dropdown */}
              <div className="raki-profile" ref={menuRef}>
                <button
                  type="button"
                  className={`raki-profile__toggle${menuOpen ? " raki-profile__toggle--open" : ""}`}
                  onClick={handleToggleMenu}
                  aria-expanded={menuOpen}
                  aria-haspopup="menu"
                >
                  {currentUser.avatar ? (
                    <img
                      src={currentUser.avatar}
                      alt=""
                      className="raki-profile__avatar"
                    />
                  ) : (
                    <span
                      className="raki-profile__avatar raki-profile__avatar--fallback"
                      aria-hidden="true"
                    >
                      {(currentUser.first_name || currentUser.username || "?")
                        .charAt(0)
                        .toUpperCase()}
                    </span>
                  )}
                  <span className="raki-profile__name">
                    {currentUser.username}
                  </span>
                  <span className="raki-profile__caret" aria-hidden="true" />
                </button>

                {menuOpen && (
                  <div className="raki-profile__menu" role="menu">
                    <div className="raki-profile__menu-head">
                      {currentUser.avatar ? (
                        <img
                          src={currentUser.avatar}
                          alt=""
                          className="raki-profile__menu-avatar"
                        />
                      ) : (
                        <span className="raki-profile__menu-avatar raki-profile__menu-avatar--fallback">
                          {(
                            currentUser.first_name ||
                            currentUser.username ||
                            "?"
                          )
                            .charAt(0)
                            .toUpperCase()}
                        </span>
                      )}
                      <div className="raki-profile__menu-meta">
                        <span className="raki-profile__menu-username">
                          {currentUser.username}
                        </span>
                        {(currentUser.first_name || currentUser.last_name) && (
                          <span className="raki-profile__menu-fullname">
                            {[currentUser.first_name, currentUser.last_name]
                              .filter(Boolean)
                              .join(" ")}
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      type="button"
                      className="raki-profile__item"
                      role="menuitem"
                      onClick={handleDecksClick}
                    >
                      {t("header.my_decks")}
                    </button>

                    <button
                      type="button"
                      className="raki-profile__item"
                      role="menuitem"
                      onClick={handleProfileClick}
                    >
                      {t("header.my_profile")}
                    </button>

                    <button
                      type="button"
                      className="raki-profile__item"
                      role="menuitem"
                      onClick={handleWalletClick}
                    >
                      {t("header.wallet")}
                    </button>

                    <button
                      type="button"
                      className="raki-profile__item"
                      role="menuitem"
                      onClick={handleSettingClick}
                    >
                      {t("header.settings")}
                    </button>

                    <button
                      type="button"
                      className="raki-profile__item raki-profile__item--danger"
                      role="menuitem"
                      onClick={logout}
                    >
                      {t("header.logout")}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
