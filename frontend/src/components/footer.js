import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="raki-footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>About Raki</h3>
          <p>Raki is an interactive flashcard app to help you study effectively.</p>
        </div>

        <div className="footer-section">
          <h3>Links</h3>
          <ul>



          </ul>
        </div>

        <div className="footer-section">
          <h3>Contact</h3>
          <p>Email: support@raki.com</p>
          <p>Phone: +84 123 456 789</p>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} Raki. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
