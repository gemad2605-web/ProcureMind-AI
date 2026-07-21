// frontend/src/components/chat/SuggestedQuestions.jsx
/**
 * 💡 الأسئلة المقترحة - Suggested Questions
 * 
 * يعرض قائمة بالأسئلة المقترحة للمساعدة في بدء المحادثة
 */

import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  MessageCircle, 
  RefreshCw, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  TrendingUp,
  FileText,
  Building2,
  Star,
  Zap,
  BookOpen,
  Shield,
  FileCheck,
  BarChart3,
  Users,
  DollarSign,
  Award,
  ClipboardList,
  GitBranch,
  Lightbulb
} from 'lucide-react';


// ============================================================
// 1. بيانات الأسئلة الافتراضية
// ============================================================

const DEFAULT_QUESTIONS = [
  {
    id: 'q1',
    question: 'ما هي شروط عقد Alpha Inc؟',
    category: 'contracts',
    icon: <FileCheck size={16} />,
    tags: ['عقد', 'شروط', 'Alpha Inc']
  },
  {
    id: 'q2',
    question: 'مين أفضل مورد حسب تقارير الجودة؟',
    category: 'quality',
    icon: <Star size={16} />,
    tags: ['جودة', 'تقييم', 'موردين']
  },
  {
    id: 'q3',
    question: 'إيه سياسة تقييم الموردين؟',
    category: 'policies',
    icon: <Shield size={16} />,
    tags: ['سياسة', 'تقييم', 'موردين']
  },
  {
    id: 'q4',
    question: 'قارن بين عروض أسعار Alpha Inc و Beta Supplies',
    category: 'quotations',
    icon: <DollarSign size={16} />,
    tags: ['عروض', 'أسعار', 'مقارنة']
  },
  {
    id: 'q5',
    question: 'ما هي قيمة عقد Gamma Co؟',
    category: 'contracts',
    icon: <FileCheck size={16} />,
    tags: ['عقد', 'قيمة', 'Gamma Co']
  },
  {
    id: 'q6',
    question: 'تقرير جودة Delta Logistics',
    category: 'quality',
    icon: <BarChart3 size={16} />,
    tags: ['جودة', 'تقرير', 'Delta Logistics']
  },
  {
    id: 'q7',
    question: 'إجراءات الشراء في المؤسسة',
    category: 'policies',
    icon: <ClipboardList size={16} />,
    tags: ['شراء', 'إجراءات', 'مشتريات']
  },
  {
    id: 'q8',
    question: 'كم عدد الموردين المسجلين؟',
    category: 'suppliers',
    icon: <Users size={16} />,
    tags: ['موردين', 'إحصائيات']
  },
  {
    id: 'q9',
    question: 'ما هي مدة عقد Epsilon Group؟',
    category: 'contracts',
    icon: <Clock size={16} />,
    tags: ['عقد', 'مدة', 'Epsilon Group']
  },
  {
    id: 'q10',
    question: 'أفضل مورد من حيث السعر والجودة',
    category: 'suppliers',
    icon: <Award size={16} />,
    tags: ['موردين', 'سعر', 'جودة']
  },
  {
    id: 'q11',
    question: 'سياسة المشتريات العامة',
    category: 'policies',
    icon: <BookOpen size={16} />,
    tags: ['سياسة', 'مشتريات', 'عامة']
  },
  {
    id: 'q12',
    question: 'تحليل أداء الموردين هذا الربع',
    category: 'quality',
    icon: <TrendingUp size={16} />,
    tags: ['تحليل', 'موردين', 'ربع سنوي']
  }
];


// ============================================================
// 2. مكون زر التصنيف
// ============================================================

const CategoryFilter = ({ categories, selectedCategory, onSelect }) => {
  const categoryLabels = {
    'all': { label: 'الكل', icon: <Sparkles size={14} /> },
    'contracts': { label: 'عقود', icon: <FileCheck size={14} /> },
    'policies': { label: 'سياسات', icon: <Shield size={14} /> },
    'quotations': { label: 'عروض', icon: <DollarSign size={14} /> },
    'quality': { label: 'جودة', icon: <Star size={14} /> },
    'suppliers': { label: 'موردين', icon: <Users size={14} /> }
  };

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {categories.map((cat) => {
        const info = categoryLabels[cat] || { label: cat, icon: <Sparkles size={14} /> };
        const isSelected = selectedCategory === cat;
        
        return (
          <button
            key={cat}
            onClick={() => onSelect(cat)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-full transition-all ${
              isSelected
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {info.icon}
            {info.label}
          </button>
        );
      })}
    </div>
  );
};


// ============================================================
// 3. مكون بطاقة السؤال
// ============================================================

const QuestionCard = ({ question, onClick, index }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={() => onClick(question.question)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`group w-full text-right p-3 rounded-xl border transition-all duration-200 ${
        isHovered
          ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20 shadow-md'
          : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50 hover:border-blue-200 dark:hover:border-blue-800'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* أيقونة */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
          isHovered
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
        }`}>
          {question.icon || <Lightbulb size={16} />}
        </div>

        {/* النص */}
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium transition-colors ${
            isHovered
              ? 'text-blue-700 dark:text-blue-300'
              : 'text-gray-800 dark:text-gray-200'
          }`}>
            {question.question}
          </p>
          
          {/* العلامات */}
          {question.tags && question.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {question.tags.slice(0, 3).map((tag, i) => (
                <span
                  key={i}
                  className="text-[10px] px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-full"
                >
                  #{tag}
                </span>
              ))}
              {question.tags.length > 3 && (
                <span className="text-[10px] text-gray-400 dark:text-gray-500">
                  +{question.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>

        {/* سهم */}
        <div className={`flex-shrink-0 transition-all duration-200 ${
          isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-2'
        }`}>
          <ChevronLeft size={16} className="text-blue-500" />
        </div>
      </div>
    </button>
  );
};


// ============================================================
// 4. مكون الأسئلة المقترحة (الرئيسي)
// ============================================================

export const SuggestedQuestions = ({
  questions = null,
  onSelect,
  title = '💡 أسئلة مقترحة',
  showCategories = true,
  maxDisplay = 6,
  className = '',
  refreshInterval = null
}) => {
  // ============================================================
  // الحالة (State)
  // ============================================================
  
  const [allQuestions] = useState(questions || DEFAULT_QUESTIONS);
  const [filteredQuestions, setFilteredQuestions] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [currentPage, setCurrentPage] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // ============================================================
  // التأثيرات (Effects)
  // ============================================================
  
  // تصفية الأسئلة
  useEffect(() => {
    let filtered = allQuestions;
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(q => q.category === selectedCategory);
    }
    
    // ترتيب عشوائي
    const shuffled = [...filtered].sort(() => Math.random() - 0.5);
    setFilteredQuestions(shuffled);
    setCurrentPage(0);
  }, [selectedCategory, allQuestions]);

  // تحديث تلقائي
  useEffect(() => {
    if (refreshInterval) {
      const interval = setInterval(() => {
        handleRefresh();
      }, refreshInterval);
      
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  // ============================================================
  // الدوال (Functions)
  // ============================================================
  
  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
  };

  const handleQuestionClick = (question) => {
    onSelect?.(question);
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    
    // إعادة ترتيب عشوائي
    const shuffled = [...filteredQuestions].sort(() => Math.random() - 0.5);
    setFilteredQuestions(shuffled);
    
    setTimeout(() => {
      setIsRefreshing(false);
    }, 500);
  };

  const handleNextPage = () => {
    if ((currentPage + 1) * maxDisplay < filteredQuestions.length) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1);
    }
  };

  // ============================================================
  // الحسابات
  // ============================================================
  
  const categories = ['all', ...new Set(allQuestions.map(q => q.category))];
  
  const startIndex = currentPage * maxDisplay;
  const endIndex = Math.min(startIndex + maxDisplay, filteredQuestions.length);
  const currentQuestions = filteredQuestions.slice(startIndex, endIndex);
  
  const totalPages = Math.ceil(filteredQuestions.length / maxDisplay);
  const hasNext = currentPage < totalPages - 1;
  const hasPrev = currentPage > 0;

  // ============================================================
  // العرض
  // ============================================================
  
  if (filteredQuestions.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">
          لا توجد أسئلة مقترحة في هذا التصنيف
        </p>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* الرأس */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">{title}</span>
          <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
            {filteredQuestions.length}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-1.5 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
            title="تحديث الأسئلة"
          >
            <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* تصفية التصنيفات */}
      {showCategories && (
        <CategoryFilter
          categories={categories}
          selectedCategory={selectedCategory}
          onSelect={handleCategorySelect}
        />
      )}

      {/* قائمة الأسئلة */}
      <div className="space-y-2">
        {currentQuestions.map((question, index) => (
          <QuestionCard
            key={question.id || index}
            question={question}
            onClick={handleQuestionClick}
            index={index}
          />
        ))}
      </div>

      {/* التنقل بين الصفحات */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <button
            onClick={handlePrevPage}
            disabled={!hasPrev}
            className={`p-2 rounded-lg transition-colors ${
              hasPrev
                ? 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                : 'text-gray-300 dark:text-gray-600 cursor-not-allowed'
            }`}
          >
            <ChevronRight size={20} />
          </button>
          
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {currentPage + 1} / {totalPages}
          </span>
          
          <button
            onClick={handleNextPage}
            disabled={!hasNext}
            className={`p-2 rounded-lg transition-colors ${
              hasNext
                ? 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                : 'text-gray-300 dark:text-gray-600 cursor-not-allowed'
            }`}
          >
            <ChevronLeft size={20} />
          </button>
        </div>
      )}
    </div>
  );
};


// ============================================================
// 5. مكون عرض سريع (للصفحة الرئيسية)
// ============================================================

export const QuickSuggestions = ({ onSelect, maxDisplay = 4 }) => {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    // اختيار أسئلة عشوائية
    const shuffled = [...DEFAULT_QUESTIONS].sort(() => Math.random() - 0.5);
    setQuestions(shuffled.slice(0, maxDisplay));
  }, [maxDisplay]);

  return (
    <div className="flex flex-wrap gap-2">
      {questions.map((q) => (
        <button
          key={q.id}
          onClick={() => onSelect?.(q.question)}
          className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700 flex items-center gap-2"
        >
          {q.icon}
          {q.question}
        </button>
      ))}
    </div>
  );
};


// ============================================================
// 6. تصدير المكونات
// ============================================================

export default SuggestedQuestions;
