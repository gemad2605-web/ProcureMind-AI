import React, { useEffect, useRef } from "react";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import ChatContainer from "../components/chat/ChatContainer";
import EmptyState from "../components/common/EmptyState";
import { useChat } from "../context/ChatContext";
import { useLanguage } from "../context/LanguageContext";

/**
 * Home
 * الصفحة الرئيسية للتطبيق — تجمع بين الـ Navbar والمحادثة والـ Footer
 * مسؤولة عن التخطيط العام فقط، بينما منطق المحادثة بالكامل
 * مُدار داخل ChatContext حفاظاً على فصل الاهتمامات (Separation of Concerns)
 */
const Home = () => {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  const { language } = useLanguage();
  const scrollAnchorRef = useRef(null);

  const isRTL = language === "ar";
  const hasMessages = messages.length > 0;

  // تمرير تلقائي لآخر رسالة عند إضافة رسالة جديدة
  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const text = {
    ar: {
      errorBanner: "حدث خطأ في الاتصال بالخادم. برجاء المحاولة مرة أخرى.",
      dismiss: "إغلاق",
      newChat: "محادثة جديدة",
    },
    en: {
      errorBanner: "A server connection error occurred. Please try again.",
      dismiss: "Dismiss",
      newChat: "New chat",
    },
  };

  const t = text[language] || text.ar;

  return (
    <div
      dir={isRTL ? "rtl" : "ltr"}
      className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors"
    >
      <Navbar />

      <main className="flex-1 flex flex-col w-full max-w-4xl mx-auto px-4 sm:px-6 py-6">
        {/* شريط خطأ عام (مستقل عن أخطاء الرسائل الفردية) */}
        {error && (
          <div
            role="alert"
            className="flex items-center justify-between gap-3 mb-4 px-4 py-3 rounded-lg border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 text-sm animate-in fade-in"
          >
            <span>{t.errorBanner}</span>
          </div>
        )}

        {/* رأس الصفحة: زرار محادثة جديدة يظهر فقط لو فيه محادثة قائمة */}
        {hasMessages && (
          <div className="flex justify-end mb-3">
            <button
              onClick={clearChat}
              className="text-xs px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {t.newChat}
            </button>
          </div>
        )}

        {/* المحتوى الرئيسي: حالة فارغة أو محادثة نشطة */}
        <section className="flex-1 flex flex-col min-h-0">
          {hasMessages ? (
            <>
              <ChatContainer
                messages={messages}
                isLoading={isLoading}
                onSendMessage={sendMessage}
              />
              <div ref={scrollAnchorRef} />
            </>
          ) : (
            <EmptyState onSuggestionClick={sendMessage} />
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Home;
