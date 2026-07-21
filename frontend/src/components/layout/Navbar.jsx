import React from "react";
import { useLanguage } from "../../context/LanguageContext"; // هيتعمل لاحقاً
import { useTheme } from "../../context/ThemeContext"; // هيتعمل لاحقاً

const Navbar = () => {
  const { language, toggleLanguage } = useLanguage
    ? useLanguage()
    : { language: "ar", toggleLanguage: () => {} }; // fallback مؤقت

  const { theme, toggleTheme } = useTheme
    ? useTheme()
    : { theme: "light", toggleTheme: () => {} }; // fallback مؤقت

  const text = {
    ar: {
      title: "ProcureMind-AI",
      subtitle: "مساعد المشتريات الذكي",
    },
    en: {
      title: "ProcureMind-AI",
      subtitle: "Smart Procurement Assistant",
    },
  };

  const t = text[language] || text.ar;

  return (
    <nav className="w-full border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-6 py-3 transition-colors">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* الشعار والعنوان */}
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="ProcureMind-AI" className="w-8 h-8" />
          <div className="flex flex-col leading-tight">
            <span className="font-bold text-gray-800 dark:text-gray-100 text-lg">
              {t.title}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {t.subtitle}
            </span>
          </div>
        </div>

        {/* الأزرار */}
        <div className="flex items-center gap-3">
          {/* زرار تبديل اللغة */}
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle language"
          >
            🌐 {language === "ar" ? "EN" : "عربي"}
          </button>

          {/* زرار الوضع الليلي/النهاري */}
          <button
            onClick={toggleTheme}
            className="flex items-center justify-center w-9 h-9 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle dark mode"
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
