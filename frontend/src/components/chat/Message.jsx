// frontend/src/components/chat/Message.jsx
/**
 * 💬 عرض رسالة واحدة - Message Component
 * 
 * يعرض رسالة المستخدم أو المساعد مع المصادر والإجراءات
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  User, 
  Bot, 
  Copy, 
  Check, 
  ThumbsUp, 
  ThumbsDown,
  RefreshCw,
  FileText,
  ExternalLink,
  Sparkles,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';
import { Sources } from './Sources';


// ============================================================
// 1. مكون الرمز (Avatar)
// ============================================================

const MessageAvatar = ({ role }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
      isUser 
        ? 'bg-gradient-to-r from-green-400 to-emerald-500' 
        : 'bg-gradient-to-r from-blue-500 to-indigo-600'
    }`}>
      {isUser ? (
        <User size={16} className="text-white" />
      ) : (
        <Bot size={16} className="text-white" />
      )}
    </div>
  );
};


// ============================================================
// 2. مكون الإجراءات (Actions)
// ============================================================

const MessageActions = ({ 
  content, 
  onCopy, 
  onLike, 
  onDislike, 
  onRegenerate,
  isCopied,
  isLast,
  isAssistant,
  sources 
}) => {
  if (!isAssistant) return null;

  return (
    <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      {/* زر النسخ */}
      <button
        onClick={onCopy}
        className="p-1.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        title="نسخ"
      >
        {isCopied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
      </button>

      {/* زر الإعجاب */}
      <button
        onClick={onLike}
        className="p-1.5 text-gray-400 hover:text-green-600 dark:text-gray-500 dark:hover:text-green-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        title="مفيد"
      >
        <ThumbsUp size={14} />
      </button>

      {/* زر عدم الإعجاب */}
      <button
        onClick={onDislike}
        className="p-1.5 text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        title="غير مفيد"
      >
        <ThumbsDown size={14} />
      </button>

      {/* زر إعادة التوليد (لآخر رسالة فقط) */}
      {isLast && (
        <button
          onClick={onRegenerate}
          className="p-1.5 text-gray-400 hover:text-indigo-600 dark:text-gray-500 dark:hover:text-indigo-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          title="إعادة توليد"
        >
          <RefreshCw size={14} />
        </button>
      )}
    </div>
  );
};


// ============================================================
// 3. مكون الوقت والمصادر
// ============================================================

const MessageFooter = ({ timestamp, sources, showSources, onToggleSources }) => {
  if (!timestamp && !sources) return null;

  const hasSources = sources && sources.length > 0;

  return (
    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
      {/* الوقت */}
      {timestamp && (
        <span className="flex items-center gap-1">
          <Clock size={12} />
          {timestamp}
        </span>
      )}

      {/* المصادر */}
      {hasSources && (
        <button
          onClick={onToggleSources}
          className="flex items-center gap-1 text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
        >
          <FileText size={12} />
          <span>{showSources ? 'إخفاء المصادر' : `عرض المصادر (${sources.length})`}</span>
          {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
      )}
    </div>
  );
};


// ============================================================
// 4. مكون المحتوى مع تنسيق النص
// ============================================================

const FormattedContent = ({ content }) => {
  // تنسيق النص (روابط، نقاط، خطوط)
  const formatText = (text) => {
    if (!text) return null;

    // تقسيم إلى فقرات
    const paragraphs = text.split('\n').filter(p => p.trim());

    return paragraphs.map((paragraph, index) => {
      // التحقق من النقاط
      if (paragraph.trim().startsWith('•') || paragraph.trim().startsWith('-') || paragraph.trim().startsWith('*')) {
        return (
          <div key={index} className="flex items-start gap-2 my-1">
            <span className="text-blue-500">•</span>
            <span className="flex-1">{paragraph.trim().substring(1).trim()}</span>
          </div>
        );
      }

      // التحقق من العناوين
      if (paragraph.trim().startsWith('## ')) {
        return (
          <h4 key={index} className="font-semibold text-gray-800 dark:text-gray-200 mt-3 mb-1">
            {paragraph.trim().substring(3)}
          </h4>
        );
      }

      if (paragraph.trim().startsWith('### ')) {
        return (
          <h5 key={index} className="font-medium text-gray-700 dark:text-gray-300 mt-2 mb-1">
            {paragraph.trim().substring(4)}
          </h5>
        );
      }

      // نص عادي
      return (
        <p key={index} className="my-1 leading-relaxed">
          {paragraph}
        </p>
      );
    });
  };

  return <div className="whitespace-pre-wrap break-words">{formatText(content)}</div>;
};


// ============================================================
// 5. مكون رسالة الخطأ
// ============================================================

const ErrorMessage = ({ content }) => {
  return (
    <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
      <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
      <div>
        <p className="text-sm font-medium text-red-800 dark:text-red-200">
          حدث خطأ
        </p>
        <p className="text-sm text-red-600 dark:text-red-300">
          {content}
        </p>
      </div>
    </div>
  );
};


// ============================================================
// 6. المكون الرئيسي - Message
// ============================================================

export const Message = ({ 
  message, 
  isLast = false,
  sources = [],
  onLike,
  onDislike,
  onRegenerate,
  onCopy
}) => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const [isCopied, setIsCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  // ============================================================
  // استخراج البيانات
  // ============================================================
  
  const { role, content, timestamp } = message;
  const isUser = role === 'user';
  const isAssistant = role === 'assistant' || role === 'bot';
  const isError = role === 'error';
  const hasSources = sources && sources.length > 0;

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
      onCopy?.(content);
    } catch (error) {
      console.error('❌ فشل في النسخ:', error);
    }
  };

  const handleLike = () => {
    onLike?.(message);
  };

  const handleDislike = () => {
    onDislike?.(message);
  };

  const handleRegenerate = () => {
    onRegenerate?.();
  };

  const toggleSources = () => {
    setShowSources(!showSources);
  };

  // ============================================================
  // تنسيق الوقت
  // ============================================================
  
  const formatTimestamp = (ts) => {
    if (!ts) return '';
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return ts;
    }
  };

  // ============================================================
  // العرض
  // ============================================================
  
  // رسالة الخطأ
  if (isError) {
    return <ErrorMessage content={content} />;
  }

  // تنسيق الرسالة حسب الدور
  const messageClasses = isUser 
    ? 'ml-auto max-w-[85%] bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl rounded-tr-none'
    : 'max-w-[85%] bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-2xl rounded-tl-none shadow-sm border border-gray-200 dark:border-gray-700';

  return (
    <div 
      className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* الرمز */}
      {!isUser && <MessageAvatar role="assistant" />}
      {isUser && <MessageAvatar role="user" />}

      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        {/* المحتوى */}
        <div className={`group relative ${messageClasses}`}>
          <div className="px-4 py-3">
            {isAssistant && (
              <div className="flex items-center gap-2 mb-1">
                <Sparkles size={14} className="text-blue-500 dark:text-blue-400" />
                <span className="text-xs font-medium text-blue-500 dark:text-blue-400">
                  ProcureMind
                </span>
              </div>
            )}
            
            <FormattedContent content={content} />
            
            {/* الإجراءات */}
            <div className={`${isHovered || isLast ? 'opacity-100' : 'opacity-0'} transition-opacity`}>
              <MessageActions
                content={content}
                onCopy={handleCopy}
                onLike={handleLike}
                onDislike={handleDislike}
                onRegenerate={handleRegenerate}
                isCopied={isCopied}
                isLast={isLast}
                isAssistant={isAssistant}
                sources={sources}
              />
            </div>
          </div>
        </div>

        {/* التذييل (الوقت والمصادر) */}
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mt-1 px-1`}>
          <MessageFooter
            timestamp={formatTimestamp(timestamp)}
            sources={sources}
            showSources={showSources}
            onToggleSources={toggleSources}
          />
        </div>

        {/* عرض المصادر الموسع */}
        {showSources && hasSources && (
          <div className="mt-2">
            <Sources sources={sources} />
          </div>
        )}
      </div>
    </div>
  );
};


// ============================================================
// 7. تصدير المكون
// ============================================================

export default Message;
