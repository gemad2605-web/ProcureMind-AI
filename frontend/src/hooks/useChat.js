import { useState, useCallback, useRef } from "react";
import { sendMessage as sendMessageAPI } from "../api/procuremind"; // هيتعمل لاحقاً

/**
 * useChat
 * خطاف مستقل لإدارة منطق المحادثة (رسائل، تحميل، أخطاء، إعادة محاولة)
 * يمكن استخدامه مباشرة داخل أي مكون، أو تغليفه داخل ChatContext لمشاركة الحالة عالمياً
 */
const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const lastFailedMessageRef = useRef(null);

  const sendMessage = useCallback(async (text) => {
    if (!text || !text.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    lastFailedMessageRef.current = null;

    try {
      const response = await sendMessageAPI(text);

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response?.answer || "",
        sources: response?.sources || [],
        suggestedQuestions: response?.suggested_questions || [],
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      return assistantMessage;
    } catch (err) {
      const errorMsg = err?.message || "حدث خطأ أثناء إرسال الرسالة";
      setError(errorMsg);
      lastFailedMessageRef.current = text;

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: "عذراً، حدث خطأ أثناء معالجة طلبك. حاول مرة أخرى.",
        isError: true,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const retryLastMessage = useCallback(() => {
    if (lastFailedMessageRef.current) {
      return sendMessage(lastFailedMessageRef.current);
    }
  }, [sendMessage]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    lastFailedMessageRef.current = null;
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    retryLastMessage,
    clearChat,
  };
};

export default useChat;
