import React, { useState, useContext, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AuthContext } from "../../../context/AuthContext.js";
import "./Header.css";
import Button from "../../../components/Common/Button/Button.js";

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
            <a href="/" className="raki-logo">
              <span className="raki-logo__text">
                <span className="raki-logo__accent">ra</span>ki
              </span>
            </a>
          </div>

          <nav className="raki-nav-links">
            <Link to="/decks" className="raki-nav-item">
              {t("header.MY_DECKS")}
            </Link>

            <Link to="/community" className="raki-nav-item">
              {t("header.COMMUNITY")}
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
                className="raki-profile__toggle"
                onClick={handleToggleMenu}
              >
                {currentUser.username}
              </button>

              {menuOpen && (
                <div className="raki-profile__menu">
                  <button
                    className="raki-profile__item"
                    onClick={handleDecksClick}
                  >
                    {t("header.my_decks")}
                  </button>

                  <button
                    className="raki-profile__item"
                    onClick={handleProfileClick}
                  >
                    {t("header.my_profile")}
                  </button>

                  <button
                    className="raki-profile__item"
                    onClick={handleWalletClick}
                  >
                    {t("header.wallet")}
                  </button>

                  <button
                    className="raki-profile__item"
                    onClick={handleSettingClick}
                  >
                    {t("header.settings")}
                  </button>

                  <button
                    className="raki-profile__item raki-profile__item--danger"
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
