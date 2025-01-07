// i18n.js

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import HttpApi from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

i18n
  .use(HttpApi)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: ["en", "he"],
    fallbackLng: "en",
    detection: {
      order: ["queryString", "cookie", "localStorage", "navigator"],
      caches: ["cookie"],
    },
    backend: {
      loadPath: "/assets/locales/{{lng}}/translation.json",
    },
    interpolation: {
      escapeValue: false,
    },
    // lng: "he",
  });

if (typeof window !== "undefined") {
  window.t = i18n.t;
}

export default i18n;
