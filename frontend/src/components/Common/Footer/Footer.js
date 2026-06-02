import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "./Footer.css";

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="raki-footer">
      <div className="container raki-footer__inner">
        {/* LEFT */}
        <div className="raki-footer__brand">
          <div className="raki-footer__logo">
            <span className="raki-footer__logo-accent">ra</span>ki
          </div>
          <p className="raki-footer__desc">{t("footer.description")}</p>
        </div>

        {/* RIGHT */}
        <div className="raki-footer__links">
          <div className="raki-footer__col">
            <h4>{t("footer.contact")}</h4>
            <p>support@raki.com</p>
            <p>+84 123 456 789</p>
          </div>
        </div>
      </div>

      {/* BOTTOM */}
      <div className="raki-footer__bottom">
        <p>{t("footer.copyright", { year: currentYear })}</p>
      </div>
    </footer>
  );
};

export default Footer;
