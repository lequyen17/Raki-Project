import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="raki-footer">
      <div className="container raki-footer__inner">
        {/* LEFT */}
        <div className="raki-footer__brand">
          <div className="raki-footer__logo">
            <span className="raki-footer__logo-accent">ra</span>ki
          </div>
          <p className="raki-footer__desc">
            Raki is an interactive flashcard app to help you study effectively.
          </p>
        </div>

        {/* RIGHT */}
        <div className="raki-footer__links">
          <div className="raki-footer__col">
            <h4>Product</h4>
            <Link to="/decks">My Decks</Link>
            <Link to="/profile">Profile</Link>
          </div>

          <div className="raki-footer__col">
            <h4>Contact</h4>
            <p>support@raki.com</p>
            <p>+84 123 456 789</p>
          </div>
        </div>
      </div>

      {/* BOTTOM */}
      <div className="raki-footer__bottom">
        <p>© {currentYear} Raki. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
