// frontend/src/api/endpoints.js
/**
 * 🌐 نقاط النهاية (Endpoints) للاتصال بالـ API
 * 
 * يحتوي على جميع مسارات API المستخدمة في التطبيق
 */

// ============================================================
// 1. الإعدادات الأساسية
// ============================================================

// رابط الخادم الأساسي
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// بادئة API
const API_PREFIX = '/api';

// الرابط الكامل
export const BASE_URL = `${API_BASE_URL}${API_PREFIX}`;

// ============================================================
// 2. نقاط النهاية (Endpoints)
// ============================================================

export const ENDPOINTS = {
  // ============================================================
  // 💬 المحادثة (Chat)
  // ============================================================
  
  chat: {
    /**
     * 💬 إرسال سؤال والحصول على رد
     * POST /api/chat
     */
    send: `${BASE_URL}/chat`,
    
    /**
     * 🌊 إرسال سؤال مع تدفق الرد
     * POST /api/chat/stream
     */
    stream: `${BASE_URL}/chat/stream`,
    
    /**
     * 📜 جلب سجل المحادثة
     * GET /api/chat/history/{session_id}
     */
    history: (sessionId) => `${BASE_URL}/chat/history/${sessionId}`,
    
    /**
     * 🗑️ حذف سجل المحادثة
     * DELETE /api/chat/history/{session_id}
     */
    clearHistory: (sessionId) => `${BASE_URL}/chat/history/${sessionId}`,
    
    /**
     * 💡 الحصول على أسئلة مقترحة
     * GET /api/chat/suggestions
     */
    suggestions: `${BASE_URL}/chat/suggestions`,
  },

  // ============================================================
  // 📄 المستندات (Documents)
  // ============================================================
  
  documents: {
    /**
     * 📋 قائمة جميع المستندات
     * GET /api/documents
     */
    list: `${BASE_URL}/documents`,
    
    /**
     * 📤 رفع مستند جديد
     * POST /api/documents/upload
     */
    upload: `${BASE_URL}/documents/upload`,
    
    /**
     * 📄 الحصول على معلومات مستند
     * GET /api/documents/{doc_id}
     */
    get: (docId) => `${BASE_URL}/documents/${docId}`,
    
    /**
     * 🗑️ حذف مستند
     * DELETE /api/documents/{doc_id}
     */
    delete: (docId) => `${BASE_URL}/documents/${docId}`,
    
    /**
     * ⬇️ تحميل مستند
     * GET /api/documents/{doc_id}/download
     */
    download: (docId) => `${BASE_URL}/documents/${docId}/download`,
    
    /**
     * 🏷️ جلب جميع التصنيفات
     * GET /api/documents/categories
     */
    categories: `${BASE_URL}/documents/categories`,
    
    /**
     * 🔄 إعادة بناء الفهرس
     * POST /api/documents/reindex
     */
    reindex: `${BASE_URL}/documents/reindex`,
  },

  // ============================================================
  // 🏢 الموردين (Suppliers)
  // ============================================================
  
  suppliers: {
    /**
     * 📋 قائمة جميع الموردين
     * GET /api/suppliers
     */
    list: `${BASE_URL}/suppliers`,
    
    /**
     * 📄 الحصول على معلومات مورد
     * GET /api/suppliers/{supplier_id}
     */
    get: (supplierId) => `${BASE_URL}/suppliers/${supplierId}`,
    
    /**
     * ➕ إضافة مورد جديد
     * POST /api/suppliers
     */
    create: `${BASE_URL}/suppliers`,
    
    /**
     * ✏️ تحديث معلومات مورد
     * PUT /api/suppliers/{supplier_id}
     */
    update: (supplierId) => `${BASE_URL}/suppliers/${supplierId}`,
    
    /**
     * 🗑️ حذف مورد
     * DELETE /api/suppliers/{supplier_id}
     */
    delete: (supplierId) => `${BASE_URL}/suppliers/${supplierId}`,
  },

  // ============================================================
  // 🔍 البحث (Search)
  // ============================================================
  
  search: {
    /**
     * 🔍 البحث الدلالي
     * POST /api/search
     */
    semantic: `${BASE_URL}/search`,
    
    /**
     * 🔍 البحث بالكلمات المفتاحية
     * POST /api/search/keywords
     */
    keywords: `${BASE_URL}/search/keywords`,
    
    /**
     * 🔍 البحث الهجين (دلالي + كلمات)
     * POST /api/search/hybrid
     */
    hybrid: `${BASE_URL}/search/hybrid`,
  },

  // ============================================================
  // 🩺 الصحة (Health)
  // ============================================================
  
  health: {
    /**
     * 🩺 فحص صحة النظام
     * GET /api/health
     */
    check: `${BASE_URL}/health`,
    
    /**
     * 🔄 فحص جاهزية النظام
     * GET /api/health/readiness
     */
    readiness: `${BASE_URL}/health/readiness`,
    
    /**
     * 💓 فحص أن الخادم يعمل
     * GET /api/health/liveness
     */
    liveness: `${BASE_URL}/health/liveness`,
  },

  // ============================================================
  // 📊 التحليلات (Analytics)
  // ============================================================
  
  analytics: {
    /**
     * 📊 الحصول على إحصائيات النظام
     * GET /api/analytics
     */
    stats: `${BASE_URL}/analytics`,
    
    /**
     * 📈 الحصول على إحصائيات الموردين
     * GET /api/analytics/suppliers
     */
    suppliers: `${BASE_URL}/analytics/suppliers`,
    
    /**
     * 📉 الحصول على إحصائيات المستندات
     * GET /api/analytics/documents
     */
    documents: `${BASE_URL}/analytics/documents`,
  },

  // ============================================================
  // 🔐 المصادقة (Auth)
  // ============================================================
  
  auth: {
    /**
     * 🔐 تسجيل الدخول
     * POST /api/auth/login
     */
    login: `${BASE_URL}/auth/login`,
    
    /**
     * 🔐 تسجيل الخروج
     * POST /api/auth/logout
     */
    logout: `${BASE_URL}/auth/logout`,
    
    /**
     * 🔐 التحقق من التوكن
     * GET /api/auth/verify
     */
    verify: `${BASE_URL}/auth/verify`,
  },
};

// ============================================================
// 3. دوال مساعدة
// ============================================================

/**
 * 🔗 بناء رابط كامل
 * @param {string} endpoint - نقطة النهاية
 * @param {Object} params - معلمات الاستعلام
 * @returns {string} الرابط الكامل
 */
export const buildUrl = (endpoint, params = {}) => {
  const url = new URL(endpoint);
  
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      url.searchParams.append(key, params[key]);
    }
  });
  
  return url.toString();
};

/**
 * 🏷️ الحصول على نقطة نهاية مع معلمات
 * @param {string} endpoint - نقطة النهاية
 * @param {string|number} id - المعرف
 * @returns {string} الرابط
 */
export const withId = (endpoint, id) => {
  return `${endpoint}/${id}`;
};

/**
 * 📋 الحصول على نقطة نهاية مع تصفية
 * @param {string} endpoint - نقطة النهاية
 * @param {Object} filters - معلمات التصفية
 * @returns {string} الرابط
 */
export const withFilters = (endpoint, filters = {}) => {
  return buildUrl(endpoint, filters);
};

// ============================================================
// 4. تصدير افتراضي
// ============================================================

export default ENDPOINTS;
