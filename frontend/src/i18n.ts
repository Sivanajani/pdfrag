import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { resources } from "./i18n/resources";

const savedLang = localStorage.getItem("lang");
const browserLang = navigator.language.toLowerCase().startsWith("de") ? "de" : "en";
const initialLang = savedLang === "de" || savedLang === "en" ? savedLang : browserLang;

i18n.use(initReactI18next).init({
  resources,
  lng: initialLang,
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

void i18n.changeLanguage(initialLang);

i18n.on("languageChanged", (lng: string) => {
  localStorage.setItem("lang", lng);
});

export default i18n;
