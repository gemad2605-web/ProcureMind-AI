// frontend/src/components/chat/ChatInput.jsx
/**
 * 💬 مدخل النص - Chat Input
 * 
 * مكون إدخال النص لإرسال الرسائل مع دعم الملفات والصوت
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  X, 
  Image, 
  FileText, 
  Loader2,
  Smile,
  Zap,
  Sparkles
} from 'lucide-react';


// ============================================================
// 1. مكون زر رفع الملف
// ============================================================

const FileUploadButton = ({ onFileSelect, disabled, acceptedTypes = ".txt,.docx,.pdf" }) => {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onFileSelect) {
      onFileSelect(file);
    }
    e.target.value = ''; // إعادة تعيين
  };

  return (
    <>
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        title="رفع ملف"
      >
        <Paperclip size={20} />
      </button>
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleChange}
        accept={acceptedTypes}
        className="hidden"
      />
    </>
  );
};


// ============================================================
// 2. مكون زر التسجيل الصوتي
// ============================================================

const VoiceRecorderButton = ({ onToggle, isRecording, disabled }) => {
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      className={`p-2 rounded-lg transition-colors ${
        isRecording 
          ? 'text-red-500 bg-red-100 dark:bg-red-900/20 animate-pulse' 
          : 'text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={isRecording ? 'إيقاف التسجيل' : 'تسجيل صوتي'}
    >
      <Mic size={20} />
    </button>
  );
};


// ============================================================
// 3. مكون زر الإرسال
// ============================================================

const SendButton = ({ onClick, disabled, isLoading }) => {
  return (
    <button
      type="submit"
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`p-2.5 rounded-lg transition-all ${
        !disabled && !isLoading
          ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg hover:scale-105 active:scale-95'
          : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
      }`}
      title="إرسال"
    >
      {isLoading ? (
        <Loader2 size={20} className="animate-spin" />
      ) : (
        <Send size={20} />
      )}
    </button>
  );
};


// ============================================================
// 4. مكون الأسئلة السريعة
// ============================================================

const QuickQuestions = ({ questions, onSelect, show }) => {
  if (!show || !questions || questions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-2">
      {questions.map((q, index) => (
        <button
          key={index}
          onClick={() => onSelect(q)}
          className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700"
        >
          {q}
        </button>
      ))}
    </div>
  );
};


// ============================================================
// 5. مكون المعاينة (للملفات)
// ============================================================

const FilePreview = ({ file, onRemove }) => {
  if (!file) return null;

  const getFileIcon = () => {
    const type = file.type;
    if (type.startsWith('image/')) return <Image size={16} />;
    if (type === 'application/pdf') return <FileText size={16} />;
    if (type.includes('word') || type.includes('document')) return <FileText size={16} />;
    return <FileText size={16} />;
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
      <span className="text-blue-500">{getFileIcon()}</span>
      <span className="text-sm text-gray-700 dark:text-gray-300 truncate max-w-[150px]">
        {file.name}
      </span>
      <span className="text-xs text-gray-500 dark:text-gray-400">
        {formatSize(file.size)}
      </span>
      <button
        onClick={onRemove}
        className="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
      >
        <X size={14} />
      </button>
    </div>
  );
};


// ============================================================
// 6. المكون الرئيسي - ChatInput
// ============================================================

export const ChatInput = ({
  onSend,
  onFileUpload,
  onMicToggle,
  onQuickQuestion,
  isLoading = false,
  isRecording = false,
  isStreaming = false,
  disabled = false,
  placeholder = 'اكتب سؤالك هنا...',
  quickQuestions = [],
  showQuickQuestions = true,
  acceptedFileTypes = '.txt,.docx,.pdf',
  maxFileSize = 10 * 1024 * 1024, // 10MB
  className = '',
  autoFocus = false
}) => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // ============================================================
  // التأثيرات (Effects)
  // ============================================================
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [message]);

  // تركيز تلقائي
  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  }, [autoFocus]);

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (canSend) {
      // إذا كان هناك ملف، أرسله أولاً
      if (selectedFile) {
        onFileUpload?.(selectedFile);
        setSelectedFile(null);
      }
      
      // إرسال الرسالة
      onSend?.(message);
      setMessage('');
      setFileError(null);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
    
    // Ctrl+Enter لإرسال مع سطر جديد
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      setMessage(prev => prev + '\n');
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setMessage(value);
    
    // مؤشر الكتابة
    if (value.length > 0 && !isTyping) {
      setIsTyping(true);
    }
    
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
    }, 1000);
  };

  const handleFileSelect = (file) => {
    // التحقق من الحجم
    if (file.size > maxFileSize) {
      setFileError(`حجم الملف كبير جداً. الحد الأقصى: ${maxFileSize / 1024 / 1024}MB`);
      return;
    }
    
    setSelectedFile(file);
    setFileError(null);
    
    // يمكن إضافة معاينة للملف
    if (onFileUpload) {
      onFileUpload(file);
    }
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setFileError(null);
  };

  const handleQuickQuestion = (question) => {
    setMessage(question);
    onQuickQuestion?.(question);
  };

  // ============================================================
  // الحسابات
  // ============================================================
  
  const canSend = message.trim().length > 0 && !isLoading && !disabled;
  const isSending = isLoading || isStreaming;

  // ============================================================
  // العرض
  // ============================================================
  
  return (
    <div className={`flex flex-col ${className}`}>
      {/* أخطاء الملفات */}
      {fileError && (
        <div className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-t-lg border border-red-200 dark:border-red-800">
          <X size={16} className="cursor-pointer" onClick={() => setFileError(null)} />
          <span>{fileError}</span>
        </div>
      )}

      {/* معاينة الملف */}
      {selectedFile && (
        <div className="px-3 pt-2">
          <FilePreview file={selectedFile} onRemove={handleFileRemove} />
        </div>
      )}

      {/* نموذج الإدخال */}
      <form 
        onSubmit={handleSubmit} 
        className={`flex items-end gap-2 p-3 bg-white dark:bg-gray-900 rounded-xl transition-all ${
          isFocused ? 'ring-2 ring-blue-500 ring-opacity-50 shadow-lg' : 'shadow-sm'
        } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
      >
        {/* زر رفع الملف */}
        <FileUploadButton
          onFileSelect={handleFileSelect}
          disabled={isSending || disabled}
          acceptedTypes={acceptedFileTypes}
        />

        {/* مدخل النص */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={isSending ? 'جاري التفكير...' : placeholder}
            disabled={isSending || disabled}
            rows={1}
            className="w-full px-3 py-2 bg-transparent border-0 outline-none resize-none text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ minHeight: '44px', maxHeight: '150px' }}
          />
          
          {/* مؤشر الكتابة */}
          {isTyping && (
            <span className="absolute right-3 bottom-2 text-xs text-gray-400 dark:text-gray-500 animate-pulse">
              ✍️
            </span>
          )}
        </div>

        {/* زر التسجيل الصوتي */}
        <VoiceRecorderButton
          onToggle={onMicToggle}
          isRecording={isRecording}
          disabled={isSending || disabled}
        />

        {/* زر الإرسال */}
        <SendButton
          onClick={handleSubmit}
          disabled={!canSend}
          isLoading={isSending}
        />
      </form>

      {/* الأسئلة السريعة */}
      {showQuickQuestions && quickQuestions.length > 0 && !isSending && !disabled && (
        <QuickQuestions
          questions={quickQuestions}
          onSelect={handleQuickQuestion}
          show={message.length === 0}
        />
      )}

      {/* معلومات مساعدة */}
      <div className="flex items-center justify-between mt-2 px-1">
        <div className="flex items-center gap-4 text-xs text-gray-400 dark:text-gray-500">
          <span>Shift + Enter لإضافة سطر جديد</span>
          <span>Enter للإرسال</span>
        </div>
        <div className="text-xs text-gray-400 dark:text-gray-500">
          {message.length > 0 && (
            <span>{message.length} حرف</span>
          )}
        </div>
      </div>
    </div>
  );
};


// ============================================================
// 7. تصدير المكون
// ============================================================

export default ChatInput;
