// frontend/src/components/chat/Sources.jsx
/**
 * 📎 عرض المصادر - Sources Component
 * 
 * يعرض قائمة المصادر المستخدمة في الإجابة مع معلوماتها
 */

import React, { useState } from 'react';
import { 
  FileText, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp,
  Download,
  Eye,
  CheckCircle,
  AlertCircle,
  Star,
  Clock,
  Award,
  Building2,
  FileCheck,
  FileSpreadsheet,
  FileSearch,
  FileSignature,
  FolderOpen,
  BookOpen,
  TrendingUp,
  Shield,
  ThumbsUp,
  Zap
} from 'lucide-react';


// ============================================================
// 1. مكون أيقونة التصنيف
// ============================================================

const CategoryIcon = ({ category }) => {
  const icons = {
    'contracts': <FileSignature size={14} />,
    'policies': <Shield size={14} />,
    'quotations': <FileSpreadsheet size={14} />,
    'quality_reports': <TrendingUp size={14} />,
    'invoices': <FileText size={14} />,
    'purchase_orders': <FileCheck size={14} />,
    'manuals': <BookOpen size={14} />,
    'reports': <FileSearch size={14} />,
    'other': <FolderOpen size={14} />
  };
  
  return icons[category] || <FileText size={14} />;
};


// ============================================================
// 2. مكون بطاقة المصدر (Source Card)
// ============================================================

const SourceCard = ({ source, index, onDownload, onView }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  
  const {
    id,
    filename,
    category,
    content,
    relevance_score,
    preview,
    supplier,
    contract_value,
    quality_score,
    date_added
  } = source;

  // حساب نسبة المطابقة كلون
  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'text-green-500 bg-green-50 dark:bg-green-900/20';
    if (score >= 0.6) return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
    if (score >= 0.4) return 'text-orange-500 bg-orange-50 dark:bg-orange-900/20';
    return 'text-gray-500 bg-gray-50 dark:bg-gray-800';
  };

  // تنسيق التصنيف للعرض
  const getCategoryLabel = (cat) => {
    const labels = {
      'contracts': 'عقد',
      'policies': 'سياسة',
      'quotations': 'عرض سعر',
      'quality_reports': 'تقرير جودة',
      'invoices': 'فاتورة',
      'purchase_orders': 'أمر شراء',
      'manuals': 'دليل',
      'reports': 'تقرير',
      'other': 'أخرى'
    };
    return labels[cat] || cat;
  };

  // تنسيق القيمة النقدية
  const formatCurrency = (value) => {
    if (!value) return null;
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'SAR',
      maximumFractionDigits: 0
    }).format(value);
  };

  // الحصول على معاينة النص
  const getPreviewText = () => {
    if (preview) return preview;
    if (content) {
      const text = content.replace(/\s+/g, ' ').trim();
      return text.length > 150 ? text.substring(0, 150) + '...' : text;
    }
    return 'لا يوجد معاينة متاحة';
  };

  return (
    <div 
      className={`border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden transition-all duration-200 ${
        isHovered ? 'shadow-md border-blue-300 dark:border-blue-700' : 'shadow-sm'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* رأس المصدر */}
      <div 
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* أيقونة التصنيف */}
        <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 flex-shrink-0">
          <CategoryIcon category={category} />
        </div>

        {/* معلومات المصدر */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
              {filename}
            </h4>
            <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full whitespace-nowrap">
              {getCategoryLabel(category)}
            </span>
          </div>
          
          <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500 dark:text-gray-400">
            {/* درجة المطابقة */}
            <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${getRelevanceColor(relevance_score)}`}>
              <Zap size={12} />
              {Math.round((relevance_score || 0) * 100)}% مطابقة
            </span>

            {/* المورد */}
            {supplier && (
              <span className="flex items-center gap-1">
                <Building2 size={12} />
                {supplier}
              </span>
            )}

            {/* تاريخ الإضافة */}
            {date_added && (
              <span className="flex items-center gap-1">
                <Clock size={12} />
                {new Date(date_added).toLocaleDateString('ar-SA')}
              </span>
            )}
          </div>
        </div>

        {/* الأزرار */}
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {/* زر التحميل */}
          {onDownload && (
            <button
              onClick={() => onDownload(id)}
              className="p-1.5 text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              title="تحميل الملف"
            >
              <Download size={16} />
            </button>
          )}
          
          {/* زر العرض */}
          {onView && (
            <button
              onClick={() => onView(id)}
              className="p-1.5 text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              title="عرض الملف"
            >
              <Eye size={16} />
            </button>
          )}

          {/* زر التوسيع */}
          <button
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title={isExpanded ? 'طي' : 'توسيع'}
          >
            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {/* محتوى موسع */}
      {isExpanded && (
        <div className="p-3 pt-0 border-t border-gray-100 dark:border-gray-800">
          {/* معلومات إضافية */}
          <div className="grid grid-cols-2 gap-2 mt-3">
            {contract_value && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500 dark:text-gray-400">قيمة العقد:</span>
                <span className="font-medium text-green-600 dark:text-green-400">
                  {formatCurrency(contract_value)}
                </span>
              </div>
            )}
            
            {quality_score && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500 dark:text-gray-400">درجة الجودة:</span>
                <span className="font-medium text-blue-600 dark:text-blue-400">
                  {quality_score}%
                </span>
              </div>
            )}
          </div>

          {/* معاينة النص */}
          <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
              {getPreviewText()}
            </p>
          </div>

          {/* رابط المصدر */}
          <div className="mt-2 flex justify-end">
            <button
              onClick={() => onView?.(id)}
              className="text-xs text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
            >
              <ExternalLink size={12} />
              عرض المصدر كاملاً
            </button>
          </div>
        </div>
      )}
    </div>
  );
};


// ============================================================
// 3. مكون المصادر (الرئيسي)
// ============================================================

export const Sources = ({ 
  sources = [], 
  title = 'المصادر', 
  showCount = true,
  onDownload,
  onView,
  className = '',
  maxDisplay = 5,
  showAll = false
}) => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const [showAllSources, setShowAllSources] = useState(showAll);
  const [expandedSources, setExpandedSources] = useState({});

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const toggleShowAll = () => {
    setShowAllSources(!showAllSources);
  };

  const toggleSource = (id) => {
    setExpandedSources(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  // ============================================================
  // التحقق من وجود مصادر
  // ============================================================
  
  if (!sources || sources.length === 0) {
    return null;
  }

  // ============================================================
  // تحديد المصادر المعروضة
  // ============================================================
  
  const displaySources = showAllSources ? sources : sources.slice(0, maxDisplay);
  const hasMore = sources.length > maxDisplay && !showAllSources;

  // ============================================================
  // إحصائيات المصادر
  // ============================================================
  
  const categories = sources.reduce((acc, source) => {
    const cat = source.category || 'other';
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const avgScore = sources.reduce((acc, source) => acc + (source.relevance_score || 0), 0) / sources.length;

  // ============================================================
  // العرض
  // ============================================================
  
  return (
    <div className={`bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 ${className}`}>
      {/* رأس المصادر */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-blue-500" />
          <h3 className="font-semibold text-gray-800 dark:text-gray-200">
            {title}
          </h3>
          {showCount && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
              {sources.length}
            </span>
          )}
        </div>

        {/* إحصائيات سريعة */}
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <Zap size={12} />
            {Math.round(avgScore * 100)}% متوسط المطابقة
          </span>
          {Object.keys(categories).length > 0 && (
            <span className="flex items-center gap-1">
              <FolderOpen size={12} />
              {Object.keys(categories).length} تصنيفات
            </span>
          )}
        </div>
      </div>

      {/* قائمة المصادر */}
      <div className="space-y-2">
        {displaySources.map((source, index) => (
          <SourceCard
            key={source.id || index}
            source={source}
            index={index}
            onDownload={onDownload}
            onView={onView}
          />
        ))}
      </div>

      {/* زر عرض المزيد */}
      {hasMore && (
        <button
          onClick={toggleShowAll}
          className="mt-3 text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1 transition-colors"
        >
          عرض {sources.length - maxDisplay} مصدر إضافي
          <ChevronDown size={16} />
        </button>
      )}

      {showAllSources && sources.length > maxDisplay && (
        <button
          onClick={toggleShowAll}
          className="mt-3 text-sm text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1 transition-colors"
        >
          عرض أقل
          <ChevronUp size={16} />
        </button>
      )}
    </div>
  );
};


// ============================================================
// 4. مكون مصادر مختصرة (للرسائل)
// ============================================================

export const SourcesInline = ({ sources = [], maxDisplay = 2 }) => {
  if (!sources || sources.length === 0) return null;

  const displaySources = sources.slice(0, maxDisplay);
  const remaining = sources.length - maxDisplay;

  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <FileText size={12} />
        المصادر:
      </span>
      {displaySources.map((source, index) => (
        <span
          key={source.id || index}
          className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full truncate max-w-[120px]"
          title={source.filename}
        >
          {source.filename}
        </span>
      ))}
      {remaining > 0 && (
        <span className="text-xs text-gray-400 dark:text-gray-500">
          +{remaining} أخرى
        </span>
      )}
    </div>
  );
};


// ============================================================
// 5. تصدير المكونات
// ============================================================

export default Sources;
