// frontend/src/components/chat/MessageList.jsx
/**
 * 📜 قائمة الرسائل - Message List
 * 
 * تعرض جميع رسائل المحادثة مع إدارة التمرير التلقائي
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { 
  ChevronDown, 
  MessageSquare, 
  Sparkles,
  Loader2,
  AlertCircle,
  ArrowDown,
  Scroll
} from 'lucide-react';
import { Message } from './Message';
import { Sources } from './Sources';
import { TypingIndicator } from './TypingIndicator';


// ============================================================
// 1. مكون حالة فارغة (Empty State)
// ============================================================

const EmptyState = ({ onSuggestedQuestion, suggestions = [] }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20">
        <MessageSquare size={36} className="text-white" />
      </div>
      
      <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
        كيف يمكنني مساعدتك اليوم؟
      </h3>
      
      <p className="text-gray-500 dark:text-gray-400 max-w-md mb-6">
        اسأل عن العقود، الموردين، السياسات، أو أي شيء يتعلق بالمشتريات
      </p>
      
      {suggestions.length > 0 && (
        <div className="flex flex-wrap justify-center gap-2 max-w-2xl">
          {suggestions.slice(0, 6).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onSuggestedQuestion?.(suggestion.question || suggestion)}
              className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700"
            >
              {suggestion.question || suggestion}
            </button>
          ))}
        </div>
      )}
      
      <div className="mt-8 text-xs text-gray-400 dark:text-gray-500">
        <span className="flex items-center gap-1">
          <Sparkles size={12} />
          مدعوم بـ RAG و Grok AI
        </span>
      </div>
    </div>
  );
};


// ============================================================
// 2. مكون زر التمرير للأسفل
// ============================================================

const ScrollToBottomButton = ({ onClick, show, count }) => {
  if (!show) return null;
  
  return (
    <button
      onClick={onClick}
      className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 hover:shadow-xl transition-all duration-200 flex items-center gap-2 text-sm z-10"
    >
      <ArrowDown size={16} />
      {count > 0 && (
        <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
          {count}
        </span>
      )}
    </button>
  );
};


// ============================================================
// 3. مكون مؤشر التحميل (المحادثة)
// ============================================================

const LoadingMessages = () => {
  return (
    <div className="flex items-center justify-center py-8">
      <Loader2 size={24} className="animate-spin text-blue-500" />
      <span className="ml-3 text-gray-500 dark:text-gray-400">جاري تحميل الرسائل...</span>
    </div>
  );
};


// ============================================================
// 4. مكون خطأ التحميل
// ============================================================

const ErrorState = ({ error, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mb-4">
        <AlertCircle size={32} className="text-red-500" />
      </div>
      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
        حدث خطأ
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-sm max-w-md">
        {error || 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.'}
      </p>
      <button
        onClick={onRetry}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        إعادة المحاولة
      </button>
    </div>
  );
};


// ============================================================
// 5. المكون الرئيسي - MessageList
// ============================================================

export const MessageList = ({
  messages = [],
  sources = [],
  isLoading = false,
  isStreaming = false,
  isTyping = false,
  error = null,
  onRetry,
  onLike,
  onDislike,
  onRegenerate,
  onCopy,
  onSuggestedQuestion,
  suggestions = [],
  autoScroll = true,
  className = ''
}) => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const previousMessagesLength = useRef(messages.length);

  // ============================================================
  // التأثيرات (Effects)
  // ============================================================
  
  // التمرير التلقائي عند إضافة رسائل جديدة
  useEffect(() => {
    if (autoScroll && isAtBottom) {
      scrollToBottom();
    } else if (messages.length > previousMessagesLength.current) {
      // زيادة عدد الرسائل غير المقروءة إذا لم نكن في الأسفل
      if (!isAtBottom) {
        setUnreadCount(prev => prev + 1);
      }
    }
    previousMessagesLength.current = messages.length;
  }, [messages, autoScroll, isAtBottom]);

  // مراقبة التمرير
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isBottom = scrollHeight - scrollTop - clientHeight < 50;
      
      if (isBottom) {
        setIsAtBottom(true);
        setShowScrollButton(false);
        setUnreadCount(0);
      } else {
        setIsAtBottom(false);
        setShowScrollButton(true);
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // التمرير عند بدء التدفق
  useEffect(() => {
    if (isStreaming && isAtBottom) {
      scrollToBottom();
    }
  }, [isStreaming, isAtBottom]);

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setIsAtBottom(true);
    setShowScrollButton(false);
    setUnreadCount(0);
  }, []);

  const handleScrollButtonClick = () => {
    scrollToBottom();
  };

  const handleSuggestedQuestion = (question) => {
    onSuggestedQuestion?.(question);
  };

  // ============================================================
  // العرض
  // ============================================================
  
  // عرض حالة التحميل
  if (isLoading && messages.length === 0) {
    return <LoadingMessages />;
  }

  // عرض حالة الخطأ
  if (error && messages.length === 0) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  // ============================================================
  // الحصول على الرسالة الأخيرة
  // ============================================================
  
  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
  const isLastAssistant = lastMessage?.role === 'assistant' || lastMessage?.role === 'bot';

  // ============================================================
  // العرض الرئيسي
  // ============================================================
  
  return (
    <div className={`relative flex-1 overflow-hidden ${className}`}>
      {/* حاوية الرسائل */}
      <div
        ref={messagesContainerRef}
        className="h-full overflow-y-auto px-4 py-4 space-y-4 scroll-smooth"
      >
        {messages.length === 0 ? (
          // حالة فارغة
          <EmptyState 
            onSuggestedQuestion={handleSuggestedQuestion}
            suggestions={suggestions}
          />
        ) : (
          // عرض الرسائل
          <>
            {/* تجميع الرسائل حسب التاريخ (إذا كان لدينا تواريخ) */}
            {messages.map((message, index) => {
              const isLast = index === messages.length - 1;
              const messageSources = isLast ? sources : [];
              
              return (
                <Message
                  key={index}
                  message={message}
                  isLast={isLast}
                  sources={isLastAssistant ? messageSources : []}
                  onLike={onLike}
                  onDislike={onDislike}
                  onRegenerate={isLast && isLastAssistant ? onRegenerate : undefined}
                  onCopy={onCopy}
                />
              );
            })}
            
            {/* مؤشر الكتابة */}
            {(isTyping || isStreaming) && (
              <TypingIndicator />
            )}
            
            {/* نقطة نهاية الرسائل */}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* زر التمرير للأسفل */}
      <ScrollToBottomButton
        show={showScrollButton}
        onClick={handleScrollButtonClick}
        count={unreadCount}
      />
    </div>
  );
};


// ============================================================
// 6. مكون TypingIndicator (مؤشر الكتابة)
// ============================================================

const TypingIndicator = () => {
  return (
    <div className="flex items-start gap-3 px-4 py-3 max-w-[85%]">
      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
        <Sparkles size={16} className="text-white" />
      </div>
      <div className="flex items-center gap-1 px-4 py-3 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-none">
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    </div>
  );
};


// ============================================================
// 7. تصدير المكونات
// ============================================================

export default MessageList;
