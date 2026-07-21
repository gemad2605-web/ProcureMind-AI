import React, { createContext, useContext, useState, useCallback } from "react";
import { sendMessage as sendMessageAPI } from "../api/procuremind"; // هيتعمل لاحقاً

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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

    try {
      const response = await sendMessageAPI(text);

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response?.answer || "",
        sources: response?.sources || [],
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err?.message || "حدث خطأ أثناء إرسال الرسالة");

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: "عذراً، حدث خطأ أثناء معالجة طلبك. حاول مرة أخرى.",
        isError: true,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const value = {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};

export default ChatContext;
