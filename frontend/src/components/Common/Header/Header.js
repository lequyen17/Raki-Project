import React, { useState, useContext, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthContext } from "../../../context/AuthContext.js";
import "./Header.css";

const Header = () => {
  const { t } = useTranslation();
  const { currentUser, logout } = useContext(AuthContext);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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
                    {(
                      currentUser.first_name ||
                      currentUser.username ||
                      "?"
                    )
                      .charAt(0)
                      .toUpperCase()}
                  </span>
                )}
                <span className="raki-profile__name">{currentUser.username}</span>
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
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
