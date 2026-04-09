import React, { useState, useContext, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Header = () => {
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

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleProfileClick = () => {
    setMenuOpen(false);
    navigate('/profile');
  };

  const handleDecksClick = () => {
    setMenuOpen(false);
    navigate('/decks');
  };

  const handleToggleMenu = () => {
    setMenuOpen((open) => !open);
  };

  return (
    <header className="raki-header">
      <div className="raki-brand">
        <Link to="/" className="raki-logo">
          raki
        </Link>
      </div>

      <div className="raki-actions">
        {!currentUser ? (
          <div style={{display: 'flex', gap: '10px'}}>
            <Link to="/register" className="raki-button raki-button--secondary">
              Register
            </Link>
            <Link to="/login" className="raki-button raki-button--primary">
              Login
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
                  type="button"
                  className="raki-profile__item"
                  onClick={handleDecksClick}
                >
                  My Decks
                </button>
                <button
                  type="button"
                  className="raki-profile__item"
                  onClick={handleProfileClick}
                >
                  My Profile
                </button>
                <button
                  type="button"
                  className="raki-profile__item raki-profile__item--danger"
                  onClick={logout}
                >
                  Log Out
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
