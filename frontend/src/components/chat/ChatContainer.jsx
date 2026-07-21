// frontend/src/components/chat/ChatContainer.jsx
/**
 * 💬 حاوية المحادثة - Chat Container
 * 
 * المكون الرئيسي لإدارة وعرض المحادثة
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  X, 
  FileText, 
  Loader2,
  Sparkles,
  MessageSquare,
  ChevronDown,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Settings,
  User,
  Bot,
  Clock,
  Check,
  AlertCircle
} from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { Message } from './Message';
import { Sources } from './Sources';
import { SuggestedQuestions } from './SuggestedQuestions';
import procuremindAPI from '../../api/procuremind';


// ============================================================
// 1. مكون رأس المحادثة
// ============================================================

const ChatHeader = ({ 
  messageCount, 
  isLoading, 
  onClear, 
  onRefresh,
  sessionId 
}) => {
  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-t-2xl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            مساعد ProcureMind
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {messageCount > 0 ? `${messageCount} رسالة` : 'ابدأ المحادثة الآن'}
            {sessionId && (
              <span className="ml-2 text-[10px] opacity-50">
                جلسة: {sessionId.slice(-8)}
              </span>
            )}
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        {messageCount > 0 && (
          <>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
              title="تحديث"
            >
              <RefreshCw size={18} className={isLoading ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={onClear}
              className="px-3 py-1.5 text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              مسح
            </button>
          </>
        )}
      </div>
    </div>
  );
};


// ============================================================
// 2. مكون مدخل النص
// ============================================================

const ChatInput = ({ 
  onSend, 
  isLoading, 
  onFileUpload,
  onMicClick,
  isRecording 
}) => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
    }
    e.target.value = '';
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className={`flex items-end gap-2 p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 rounded-b-2xl transition-all ${
        isFocused ? 'ring-2 ring-blue-500 ring-opacity-50' : ''
      }`}
    >
      {/* زر رفع ملف */}
      <button
        type="button"
        onClick={handleFileClick}
        disabled={isLoading}
        className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
        title="رفع ملف"
      >
        <Paperclip size={20} />
      </button>
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        accept=".txt,.docx,.pdf"
        className="hidden"
      />

      {/* مدخل النص */}
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={isLoading ? 'جاري التفكير...' : 'اكتب سؤالك هنا...'}
        disabled={isLoading}
        rows={1}
        className="flex-1 px-3 py-2 bg-transparent border-0 outline-none resize-none text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ minHeight: '44px', maxHeight: '150px' }}
      />

      {/* زر تسجيل صوتي */}
      <button
        type="button"
        onClick={onMicClick}
        disabled={isLoading}
        className={`p-2 rounded-lg transition-colors ${
          isRecording 
            ? 'text-red-500 bg-red-100 dark:bg-red-900/20' 
            : 'text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
        } disabled:opacity-50`}
        title={isRecording ? 'إيقاف التسجيل' : 'تسجيل صوتي'}
      >
        <Mic size={20} />
      </button>

      {/* زر الإرسال */}
      <button
        type="submit"
        disabled={isLoading || !message.trim()}
        className={`p-2.5 rounded-lg transition-all ${
          message.trim() && !isLoading
            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg hover:scale-105'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
        }`}
      >
        {isLoading ? (
          <Loader2 size={20} className="animate-spin" />
        ) : (
          <Send size={20} />
        )}
      </button>
    </form>
  );
};


// ============================================================
// 3. مكون حالة التحميل (Typing Indicator)
// ============================================================

const TypingIndicator = () => {
  return (
    <div className="flex items-start gap-3 px-4 py-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0">
        <Bot size={16} className="text-white" />
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
// 4. مكون زر التمرير للأسفل
// ============================================================

const ScrollToBottomButton = ({ onClick, show }) => {
  if (!show) return null;
  
  return (
    <button
      onClick={onClick}
      className="absolute bottom-24 left-1/2 transform -translate-x-1/2 p-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 hover:shadow-xl transition-all duration-200 animate-bounce"
    >
      <ChevronDown size={20} />
    </button>
  );
};


// ============================================================
// 5. مكون الحاوية الرئيسية
// ============================================================

export const ChatContainer = () => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const {
    messages,
    isLoading,
    error,
    sources,
    sessionId,
    sendMessage,
    clearChat,
    regenerateLastResponse,
    isStreaming
  } = useChat();

  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  // ============================================================
  // التأثيرات (Effects)
  // ============================================================
  
  // التمرير إلى آخر رسالة
  useEffect(() => {
    if (isAtBottom) {
      scrollToBottom();
    }
  }, [messages, isAtBottom]);

  // مراقبة التمرير
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isBottom = scrollHeight - scrollTop - clientHeight < 50;
      setIsAtBottom(isBottom);
      setShowScrollButton(!isBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setIsAtBottom(true);
    setShowScrollButton(false);
  };

  const handleSend = async (text) => {
    await sendMessage(text);
  };

  const handleClear = () => {
    if (window.confirm('هل تريد مسح جميع الرسائل؟')) {
      clearChat();
    }
  };

  const handleRefresh = () => {
    if (messages.length > 0) {
      regenerateLastResponse();
    }
  };

  const handleFileUpload = async (file) => {
    setUploadingFile(true);
    try {
      const result = await procuremindAPI.documents.upload(file, {
        category: 'other',
        description: `تم الرفع من المحادثة: ${file.name}`
      });
      
      if (result.success) {
        await sendMessage(`تم رفع الملف: ${file.name}`);
      }
    } catch (error) {
      console.error('❌ خطأ في رفع الملف:', error);
    } finally {
      setUploadingFile(false);
    }
  };

  const handleMicClick = () => {
    setIsRecording(!isRecording);
    // TODO: تنفيذ التسجيل الصوتي
    if (!isRecording) {
      // بدء التسجيل
    } else {
      // إيقاف التسجيل
    }
  };

  const handleSuggestedQuestion = (question) => {
    sendMessage(question);
  };

  // ============================================================
  // عرض الحالة
  // ============================================================
  
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 p-8 text-center">
        <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mb-4">
          <AlertCircle size={32} className="text-red-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2">
          حدث خطأ
        </h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm max-w-md">
          {error}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          إعادة المحاولة
        </button>
      </div>
    );
  }

  // ============================================================
  // العرض الرئيسي
  // ============================================================
  
  return (
    <div className="flex flex-col h-[600px] bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* رأس المحادثة */}
      <ChatHeader
        messageCount={messages.length}
        isLoading={isLoading || isStreaming}
        onClear={handleClear}
        onRefresh={handleRefresh}
        sessionId={sessionId}
      />

      {/* منطقة الرسائل */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900/50"
      >
        {messages.length === 0 ? (
          // حالة فارغة
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center mb-4 shadow-lg">
              <MessageSquare size={32} className="text-white" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
              كيف يمكنني مساعدتك؟
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              اسأل عن العقود، الموردين، السياسات، أو أي شيء يتعلق بالمشتريات
            </p>
            
            {/* الأسئلة المقترحة */}
            <div className="mt-6 w-full max-w-2xl">
              <SuggestedQuestions onSelect={handleSuggestedQuestion} />
            </div>
          </div>
        ) : (
          // عرض الرسائل
          <>
            {messages.map((message, index) => (
              <Message
                key={index}
                message={message}
                isLast={index === messages.length - 1}
                sources={index === messages.length - 1 ? sources : []}
              />
            ))}
            
            {/* مؤشر التحميل */}
            {(isLoading || isStreaming) && (
              <TypingIndicator />
            )}
            
            {/* مؤشر رفع الملف */}
            {uploadingFile && (
              <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 px-4 py-2">
                <Loader2 size={16} className="animate-spin" />
                <span>جاري رفع الملف...</span>
              </div>
            )}
          </>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* زر التمرير للأسفل */}
      <ScrollToBottomButton
        show={showScrollButton}
        onClick={scrollToBottom}
      />

      {/* مدخل النص */}
      <ChatInput
        onSend={handleSend}
        isLoading={isLoading || isStreaming || uploadingFile}
        onFileUpload={handleFileUpload}
        onMicClick={handleMicClick}
        isRecording={isRecording}
      />
    </div>
  );
};

export default ChatContainer;
