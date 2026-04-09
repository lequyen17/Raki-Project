import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="raki-footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>Về Raki</h3>
          <p>Raki là ứng dụng học thẻ ghi nhớ tương tác để giúp bạn học hiệu quả hơn.</p>
        </div>

        <div className="footer-section">
          <h3>Liên kết</h3>
          <ul>
            <li><Link to="/">Trang chủ</Link></li>
            <li><Link to="/login">Đăng nhập</Link></li>
            <li><Link to="/register">Đăng ký</Link></li>
          </ul>
        </div>

        <div className="footer-section">
          <h3>Liên hệ</h3>
          <p>Email: support@raki.com</p>
          <p>Điện thoại: +84 123 456 789</p>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} Raki. Tất cả quyền được bảo lưu.</p>
      </div>
    </footer>
  );
};

export default Footer;
