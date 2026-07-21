import React from "react";
import Home from "./pages/Home";
import { ChatProvider } from "./context/ChatContext";
import { LanguageProvider } from "./context/LanguageContext"; // هيتعمل لاحقاً
import { ThemeProvider } from "./context/ThemeContext"; // هيتعمل لاحقاً
import "./styles/globals.css";

/**
 * App
 * نقطة التجميع الرئيسية لكل الـ Providers (اللغة، الوضع الليلي، المحادثة)
 * ترتيب الـ Providers مهم: Theme و Language في الخارج لأنهم يؤثروا على
 * كل التطبيق، بينما Chat بالداخل لأنه خاص بمنطق المحادثة فقط
 */
function App() {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <ChatProvider>
          <Home />
        </ChatProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
