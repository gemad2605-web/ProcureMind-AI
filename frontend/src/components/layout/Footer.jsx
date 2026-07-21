// frontend/src/components/layout/Footer.jsx

import React from "react";
import { useLanguage } from "../../context/LanguageContext"; // هيتعمل لاحقاً

const Footer = () => {
  const { language } = useLanguage
    ? useLanguage()
    : { language: "ar" }; // fallback مؤقت لحد ما نضيف LanguageContext

  const year = new Date().getFullYear();

  const text = {
    ar: {
      rights: "جميع الحقوق محفوظة",
      poweredBy: "مدعوم بواسطة",
    },
    en: {
      rights: "All rights reserved",
      poweredBy: "Powered by",
    },
  };

  const t = text[language] || text.ar;

  return (
    <footer className="w-full border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 py-4 px-6 transition-colors">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-gray-500 dark:text-gray-400">
        <span>
          © {year} ProcureMind-AI — {t.rights}
        </span>
        <span>
          {t.poweredBy} <span className="font-medium text-gray-700 dark:text-gray-300">ProcureMind-AI</span>
        </span>
      </div>
    </footer>
  );
};

export default Footer;
