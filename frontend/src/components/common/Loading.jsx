// frontend/src/components/common/Loading.jsx
/**
 * 🌀 مؤشر التحميل - Loading Component
 * 
 * يعرض مؤشرات تحميل مختلفة للاستخدام في جميع أنحاء التطبيق
 */

import React from 'react';
import { 
  Loader2, 
  Sparkles, 
  RefreshCw,
  Circle,
  Square,
  Triangle,
  Hexagon,
  Clock,
  Zap
} from 'lucide-react';


// ============================================================
// 1. مكون السبينر الأساسي
// ============================================================

export const Spinner = ({
  size = 'default',
  color = 'blue',
  className = '',
  label = 'جاري التحميل...'
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    default: 'w-8 h-8',
    large: 'w-12 h-12',
    xlarge: 'w-16 h-16'
  };

  const colorClasses = {
    blue: 'text-blue-500',
    white: 'text-white',
    gray: 'text-gray-500',
    green: 'text-green-500',
    red: 'text-red-500',
    yellow: 'text-yellow-500',
    indigo: 'text-indigo-500',
    purple: 'text-purple-500'
  };

  return (
    <div className={`flex items-center justify-center gap-3 ${className}`}>
      <Loader2 className={`${sizeClasses[size] || sizeClasses.default} ${colorClasses[color] || colorClasses.blue} animate-spin`} />
      {label && <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>}
    </div>
  );
};


// ============================================================
// 2. مكون مؤشر التحميل بالنقاط
// ============================================================

export const DotLoader = ({
  size = 'default',
  color = 'blue',
  className = '',
  count = 3,
  label = ''
}) => {
  const sizeClasses = {
    small: 'w-1.5 h-1.5',
    default: 'w-2.5 h-2.5',
    large: 'w-4 h-4'
  };

  const colorClasses = {
    blue: 'bg-blue-500',
    white: 'bg-white',
    gray: 'bg-gray-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    indigo: 'bg-indigo-500',
    purple: 'bg-purple-500'
  };

  return (
    <div className={`flex flex-col items-center gap-3 ${className}`}>
      <div className="flex items-center gap-2">
        {[...Array(count)].map((_, i) => (
          <div
            key={i}
            className={`${sizeClasses[size] || sizeClasses.default} ${colorClasses[color] || colorClasses.blue} rounded-full animate-pulse`}
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
      {label && <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>}
    </div>
  );
};


// ============================================================
// 3. مكون مؤشر التحميل بشريط
// ============================================================

export const ProgressLoader = ({
  progress = 0,
  label = 'جاري التحميل...',
  showPercentage = true,
  className = '',
  color = 'blue',
  size = 'default'
}) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    indigo: 'bg-indigo-500',
    purple: 'bg-purple-500'
  };

  const sizeClasses = {
    small: 'h-1',
    default: 'h-2',
    large: 'h-3'
  };

  return (
    <div className={`w-full max-w-md ${className}`}>
      <div className="flex justify-between mb-1">
        <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
        {showPercentage && (
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {Math.round(progress)}%
          </span>
        )}
      </div>
      <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden ${sizeClasses[size] || sizeClasses.default}`}>
        <div
          className={`${colorClasses[color] || colorClasses.blue} transition-all duration-300 ease-out rounded-full`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
    </div>
  );
};


// ============================================================
// 4. مكون مؤشر التحميل بتأثير Skeleton
// ============================================================

export const SkeletonLoader = ({
  type = 'text',
  count = 1,
  className = '',
  width = 'full',
  height = 'auto'
}) => {
  const typeClasses = {
    text: 'h-4 rounded',
    title: 'h-8 rounded-lg',
    subtitle: 'h-6 rounded-lg',
    avatar: 'w-12 h-12 rounded-full',
    card: 'h-32 rounded-xl',
    image: 'w-full h-48 rounded-xl',
    button: 'h-10 rounded-lg',
    badge: 'h-6 w-16 rounded-full'
  };

  const widthClasses = {
    full: 'w-full',
    half: 'w-1/2',
    third: 'w-1/3',
    quarter: 'w-1/4',
    '3/4': 'w-3/4'
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {[...Array(count)].map((_, i) => (
        <div
          key={i}
          className={`${typeClasses[type] || typeClasses.text} ${widthClasses[width] || widthClasses.full} bg-gray-200 dark:bg-gray-700 animate-pulse`}
          style={height !== 'auto' ? { height } : {}}
        />
      ))}
    </div>
  );
};


// ============================================================
// 5. مكون مؤشر التحميل للتطبيق بالكامل
// ============================================================

export const FullPageLoader = ({
  message = 'جاري التحميل...',
  subtitle = 'يرجى الانتظار',
  className = ''
}) => {
  return (
    <div className={`fixed inset-0 flex flex-col items-center justify-center bg-white dark:bg-gray-900 z-50 ${className}`}>
      <div className="relative">
        {/* حلقة خارجية */}
        <div className="w-20 h-20 border-4 border-blue-200 dark:border-blue-900 rounded-full" />
        
        {/* حلقة دوارة */}
        <div className="absolute top-0 left-0 w-20 h-20 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        
        {/* أيقونة في المنتصف */}
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="w-8 h-8 text-blue-500 animate-pulse" />
        </div>
      </div>
      
      <div className="mt-6 text-center">
        <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">{message}</p>
        {subtitle && (
          <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
        )}
      </div>
    </div>
  );
};


// ============================================================
// 6. مكون مؤشر التحميل للبيانات (Data Loading)
// ============================================================

export const DataLoader = ({
  rows = 3,
  columns = 4,
  showHeader = true,
  className = ''
}) => {
  return (
    <div className={`w-full ${className}`}>
      {showHeader && (
        <div className="flex items-center gap-4 mb-4">
          <SkeletonLoader type="title" width="quarter" />
          <SkeletonLoader type="text" width="half" />
        </div>
      )}
      
      <div className="space-y-3">
        {[...Array(rows)].map((_, row) => (
          <div key={row} className="flex items-center gap-4">
            {[...Array(columns)].map((_, col) => (
              <SkeletonLoader
                key={col}
                type="text"
                width="full"
                className="flex-1"
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};


// ============================================================
// 7. مكون مؤشر التحميل للزر
// ============================================================

export const ButtonLoader = ({
  size = 'default',
  color = 'white',
  className = '',
  label = ''
}) => {
  const sizeClasses = {
    small: 'w-3 h-3',
    default: 'w-4 h-4',
    large: 'w-5 h-5'
  };

  const colorClasses = {
    white: 'text-white',
    blue: 'text-blue-500',
    gray: 'text-gray-500',
    green: 'text-green-500',
    red: 'text-red-500'
  };

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <Loader2 className={`${sizeClasses[size] || sizeClasses.default} ${colorClasses[color] || colorClasses.white} animate-spin`} />
      {label && <span>{label}</span>}
    </div>
  );
};


// ============================================================
// 8. مكونات سريعة للاستخدام
// ============================================================

/**
 * 🌀 مؤشر تحميل صغير
 */
export const SmallLoader = (props) => (
  <Spinner size="small" {...props} />
);

/**
 * 🌀 مؤشر تحميل كبير
 */
export const LargeLoader = (props) => (
  <Spinner size="large" {...props} />
);

/**
 * 📄 مؤشر تحميل للصفحات
 */
export const PageLoader = ({ message = 'جاري تحميل الصفحة...' }) => (
  <div className="flex flex-col items-center justify-center py-20">
    <Spinner size="large" label={message} />
  </div>
);

/**
 * 📦 مؤشر تحميل للمكونات
 */
export const ComponentLoader = ({ height = '200px', message = '' }) => (
  <div 
    className="flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-800/50 rounded-xl"
    style={{ minHeight: height }}
  >
    <Spinner label={message} />
  </div>
);

/**
 * 📱 مؤشر تحميل للشاشات الصغيرة
 */
export const MobileLoader = ({ message = 'جاري التحميل...' }) => (
  <div className="flex items-center justify-center p-4">
    <DotLoader label={message} />
  </div>
);


// ============================================================
// 9. تصدير المكونات
// ============================================================

export default {
  Spinner,
  DotLoader,
  ProgressLoader,
  SkeletonLoader,
  FullPageLoader,
  DataLoader,
  ButtonLoader,
  SmallLoader,
  LargeLoader,
  PageLoader,
  ComponentLoader,
  MobileLoader
};
