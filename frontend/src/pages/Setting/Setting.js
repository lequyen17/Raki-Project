import React from "react";
import { useTranslation } from "react-i18next";

const Setting = () => {
  // t: hàm để dịch (translate)
  // i18n: đối tượng quản lý ngôn ngữ (để đổi tiếng, lấy tiếng hiện tại...)
  const { t, i18n } = useTranslation();

  const handleLanguageChange = (event) => {
    const selectedLanguage = event.target.value;
    i18n.changeLanguage(selectedLanguage); // Thay đổi ngôn ngữ ngay lập tức
  };

  return (
    <div className="setting" style={{ padding: "20px" }}>
      {/* 1. Dùng t('key') để dịch các tiêu đề */}
      <h1>{t("settings.title")}</h1>
      <p>{t("settings.description")}</p>

      <div className="language-selector" style={{ marginTop: "20px" }}>
        <label htmlFor="language-select" style={{ marginRight: "10px" }}>
          {t("settings.select_language")}:
        </label>

        {/* 2. Dropdown chọn ngôn ngữ */}
        <select
          id="language-select"
          value={i18n.language} // Hiển thị đúng ngôn ngữ đang dùng
          onChange={handleLanguageChange}
          style={{ padding: "5px 10px", borderRadius: "4px" }}
        >
          <option value="en">English</option>
          <option value="vi">Tiếng Việt</option>

          {/* Bạn có thể thêm các ngôn ngữ khác ở đây */}
        </select>
      </div>

      <div style={{ marginTop: "30px", color: "#666" }}>
        <small>
          {t("settings.current_lang_is")}: <strong>{i18n.language.toUpperCase()}</strong>
        </small>
      </div>
    </div>
  );
};

export default Setting;
