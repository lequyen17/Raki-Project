import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

// Import các file ngôn ngữ
import enTranslation from "./locales/en.json";
import viTranslation from "./locales/vi.json";

i18n
  // Tự động phát hiện ngôn ngữ trình duyệt hoặc từ LocalStorage
  .use(LanguageDetector)
  // Kết nối i18next với react-i18next
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslation,
      },
      vi: {
        translation: viTranslation,
      },
    },
    fallbackLng: "en", // Ngôn ngữ dự phòng khi không tìm thấy ngôn ngữ được chọn
    debug: false,
    interpolation: {
      escapeValue: false, // React đã tự bảo vệ khỏi XSS nên không cần escape
    },
  });

export default i18n;
