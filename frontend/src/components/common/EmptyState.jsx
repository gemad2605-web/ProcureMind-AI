// frontend/src/components/common/EmptyState.jsx
/**
 * 📭 حالة فارغة - Empty State
 * 
 * يعرض رسالة عندما لا توجد بيانات للعرض
 */

import React from 'react';
import { 
  Inbox, 
  FileText, 
  Search, 
  MessageSquare, 
  Users, 
  FolderOpen,
  Plus,
  RefreshCw,
  Sparkles,
  AlertCircle,
  Database,
  CloudOff,
  BookOpen,
  Filter,
  Download,
  Upload,
  Settings,
  Home,
  ArrowRight
} from 'lucide-react';


// ============================================================
// 1. أيقونات الحالات
// ============================================================

const ICONS = {
  inbox: <Inbox size={48} />,
  documents: <FileText size={48} />,
  search: <Search size={48} />,
  chat: <MessageSquare size={48} />,
  users: <Users size={48} />,
  folder: <FolderOpen size={48} />,
  database: <Database size={48} />,
  cloud: <CloudOff size={48} />,
  book: <BookOpen size={48} />,
  filter: <Filter size={48} />,
  sparkles: <Sparkles size={48} />,
  home: <Home size={48} />
};


// ============================================================
// 2. المكون الرئيسي
// ============================================================

export const EmptyState = ({
  // المحتوى الأساسي
  title = 'لا توجد بيانات',
  description = 'لم يتم العثور على أي بيانات للعرض',
  icon = 'inbox',
  iconColor = 'text-blue-500',
  
  // الإجراءات
  actionLabel = null,
  actionIcon = null,
  onAction = null,
  secondaryActionLabel = null,
  secondaryActionIcon = null,
  onSecondaryAction = null,
  
  // التخصيص
  image = null,
  imageAlt = '',
  size = 'default', // 'small', 'default', 'large'
  className = '',
  children = null,
  
  // حالة التحميل
  isLoading = false,
  loadingText = 'جاري التحميل...',
  
  // إضافات
  showRefresh = false,
  onRefresh = null,
  showHome = false,
  onHome = null,
  showUpload = false,
  onUpload = null,
  
  // تنسيق
  centered = true,
  bordered = false,
  shadow = false,
  rounded = true,
  padding = true
}) => {
  // ============================================================
  // الحجم
  // ============================================================
  
  const sizeClasses = {
    small: {
      container: 'p-6',
      icon: 'w-14 h-14',
      iconSize: 32,
      title: 'text-base',
      description: 'text-sm'
    },
    default: {
      container: 'p-8',
      icon: 'w-20 h-20',
      iconSize: 48,
      title: 'text-xl',
      description: 'text-base'
    },
    large: {
      container: 'p-12',
      icon: 'w-28 h-28',
      iconSize: 64,
      title: 'text-2xl',
      description: 'text-lg'
    }
  };

  const currentSize = sizeClasses[size] || sizeClasses.default;

  // ============================================================
  // الدوال
  // ============================================================
  
  const handleAction = () => {
    if (onAction) onAction();
  };

  const handleSecondaryAction = () => {
    if (onSecondaryAction) onSecondaryAction();
  };

  const handleRefresh = () => {
    if (onRefresh) onRefresh();
  };

  const handleHome = () => {
    if (onHome) onHome();
  };

  const handleUpload = () => {
    if (onUpload) onUpload();
  };

  // ============================================================
  // العرض
  // ============================================================
  
  const containerClasses = `
    ${centered ? 'text-center' : ''}
    ${bordered ? 'border border-gray-200 dark:border-gray-700' : ''}
    ${shadow ? 'shadow-lg' : ''}
    ${rounded ? 'rounded-xl' : ''}
    ${padding ? currentSize.container : ''}
    ${className}
  `;

  const iconWrapperClasses = `
    ${currentSize.icon}
    rounded-full 
    flex items-center justify-center 
    mx-auto mb-4
    ${iconColor} 
    bg-${iconColor.split('-')[1]}-50 dark:bg-${iconColor.split('-')[1]}-900/20
  `;

  // ============================================================
  // عرض حالة التحميل
  // ============================================================
  
  if (isLoading) {
    return (
      <div className={`flex flex-col items-center justify-center ${containerClasses}`}>
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400">{loadingText}</p>
      </div>
    );
  }

  // ============================================================
  // العرض الرئيسي
  // ============================================================
  
  return (
    <div className={`flex flex-col ${centered ? 'items-center' : ''} ${containerClasses}`}>
      {/* الصورة أو الأيقونة */}
      {image ? (
        <img 
          src={image} 
          alt={imageAlt} 
          className={`${currentSize.icon} object-contain mb-4`}
        />
      ) : (
        <div className={iconWrapperClasses}>
          {ICONS[icon] || ICONS.inbox}
        </div>
      )}

      {/* العنوان */}
      {title && (
        <h3 className={`font-semibold text-gray-800 dark:text-gray-200 ${currentSize.title}`}>
          {title}
        </h3>
      )}

      {/* الوصف */}
      {description && (
        <p className={`text-gray-500 dark:text-gray-400 mt-1 max-w-md ${currentSize.description}`}>
          {description}
        </p>
      )}

      {/* محتوى إضافي */}
      {children && (
        <div className="mt-4">
          {children}
        </div>
      )}

      {/* الأزرار */}
      {(actionLabel || secondaryActionLabel || showRefresh || showHome || showUpload) && (
        <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
          {/* زر الإجراء الرئيسي */}
          {actionLabel && (
            <button
              onClick={handleAction}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md shadow-blue-500/25"
            >
              {actionIcon || <Plus size={18} />}
              {actionLabel}
            </button>
          )}

          {/* زر الإجراء الثانوي */}
          {secondaryActionLabel && (
            <button
              onClick={handleSecondaryAction}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              {secondaryActionIcon || <ArrowRight size={18} />}
              {secondaryActionLabel}
            </button>
          )}

          {/* زر التحديث */}
          {showRefresh && (
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title="تحديث"
            >
              <RefreshCw size={20} />
            </button>
          )}

          {/* زر الصفحة الرئيسية */}
          {showHome && (
            <button
              onClick={handleHome}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title="الصفحة الرئيسية"
            >
              <Home size={20} />
            </button>
          )}

          {/* زر رفع ملف */}
          {showUpload && (
            <button
              onClick={handleUpload}
              className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title="رفع ملف"
            >
              <Upload size={20} />
            </button>
          )}
        </div>
      )}
    </div>
  );
};


// ============================================================
// 3. مكونات مخصصة للحالات المختلفة
// ============================================================

/**
 * 📄 حالة عدم وجود مستندات
 */
export const NoDocuments = (props) => (
  <EmptyState
    icon="documents"
    title="لا توجد مستندات"
    description="لم يتم العثور على أي مستندات في قاعدة المعرفة"
    actionLabel="رفع مستند"
    actionIcon={<Upload size={18} />}
    {...props}
  />
);

/**
 * 🔍 حالة عدم وجود نتائج بحث
 */
export const NoSearchResults = ({ query, ...props }) => (
  <EmptyState
    icon="search"
    title="لا توجد نتائج"
    description={`لم يتم العثور على نتائج لـ "${query}"`}
    actionLabel="بحث جديد"
    actionIcon={<Search size={18} />}
    {...props}
  />
);

/**
 * 💬 حالة عدم وجود رسائل
 */
export const NoMessages = (props) => (
  <EmptyState
    icon="chat"
    title="ابدأ المحادثة"
    description="اسأل عن أي شيء يتعلق بالمشتريات والعقود"
    actionLabel="اكتب سؤالاً"
    actionIcon={<MessageSquare size={18} />}
    {...props}
  />
);

/**
 * 🏢 حالة عدم وجود موردين
 */
export const NoSuppliers = (props) => (
  <EmptyState
    icon="users"
    title="لا توجد موردين"
    description="لم يتم العثور على أي موردين في النظام"
    actionLabel="إضافة مورد"
    actionIcon={<Plus size={18} />}
    {...props}
  />
);

/**
 * 📁 حالة عدم وجود مجلدات
 */
export const NoFolders = (props) => (
  <EmptyState
    icon="folder"
    title="لا توجد مجلدات"
    description="لم يتم العثور على أي مجلدات في هذا المسار"
    {...props}
  />
);

/**
 * 🌐 حالة عدم وجود اتصال
 */
export const NoConnection = (props) => (
  <EmptyState
    icon="cloud"
    title="لا يوجد اتصال"
    description="تعذر الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت"
    actionLabel="إعادة المحاولة"
    actionIcon={<RefreshCw size={18} />}
    iconColor="text-red-500"
    {...props}
  />
);

/**
 * 📊 حالة عدم وجود بيانات للتحليل
 */
export const NoAnalytics = (props) => (
  <EmptyState
    icon="database"
    title="لا توجد بيانات"
    description="لا توجد بيانات كافية للتحليل في الوقت الحالي"
    {...props}
  />
);

/**
 * 🎯 حالة الترحيب
 */
export const WelcomeState = ({ userName, ...props }) => (
  <EmptyState
    icon="sparkles"
    title={`مرحباً${userName ? ' ' + userName : ''}!`}
    description="كيف يمكنني مساعدتك اليوم؟ ابدأ بكتابة سؤالك"
    iconColor="text-indigo-500"
    {...props}
  />
);


// ============================================================
// 4. تصدير المكونات
// ============================================================

export default EmptyState;

