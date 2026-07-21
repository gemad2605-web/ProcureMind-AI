// frontend/src/api/procuremind.js
/**
 * 🌐 عميل API الرئيسي - ProcureMind API Client
 * 
 * يدير جميع طلبات API مع إدارة الأخطاء والمصادقة
 */

import axios from 'axios';
import ENDPOINTS from './endpoints';

// ============================================================
// 1. إعدادات العميل
// ============================================================

// رابط الخادم الأساسي
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// إنشاء عميل Axios
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 60 ثانية
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// ============================================================
// 2. Interceptors (اعتراض الطلبات)
// ============================================================

// 🔐 طلب - إضافة التوكن
apiClient.interceptors.request.use(
  (config) => {
    // إضافة التوكن من localStorage
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // إضافة معرف الجلسة
    const sessionId = localStorage.getItem('session_id');
    if (sessionId && !config.headers['X-Session-ID']) {
      config.headers['X-Session-ID'] = sessionId;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 📝 استجابة - معالجة الأخطاء
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // معالجة أخطاء المصادقة
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      // إعادة توجيه إلى صفحة تسجيل الدخول
      window.location.href = '/login';
    }
    
    // معالجة أخطاء الخادم
    if (error.response?.status >= 500) {
      console.error('❌ Server error:', error.response?.data);
    }
    
    return Promise.reject(error);
  }
);

// ============================================================
// 3. دوال مساعدة للطلبات
// ============================================================

/**
 * 🚀 طلب GET
 */
const get = async (url, params = {}) => {
  try {
    const response = await apiClient.get(url, { params });
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * 📤 طلب POST
 */
const post = async (url, data = {}, config = {}) => {
  try {
    const response = await apiClient.post(url, data, config);
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * ✏️ طلب PUT
 */
const put = async (url, data = {}, config = {}) => {
  try {
    const response = await apiClient.put(url, data, config);
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * 🗑️ طلب DELETE
 */
const del = async (url, config = {}) => {
  try {
    const response = await apiClient.delete(url, config);
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * 📤 طلب رفع ملف
 */
const upload = async (url, file, data = {}, onProgress) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // إضافة بيانات إضافية
    Object.keys(data).forEach(key => {
      formData.append(key, data[key]);
    });
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    };
    
    const response = await apiClient.post(url, formData, config);
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * 🩺 معالجة الأخطاء
 */
const handleError = (error) => {
  if (error.response) {
    // خطأ من الخادم
    const message = error.response.data?.message || 
                    error.response.data?.detail || 
                    error.response.statusText;
    return new Error(message);
  } else if (error.request) {
    // لا يوجد استجابة
    return new Error('لا يوجد اتصال بالخادم. تأكد من أن الخادم يعمل.');
  } else {
    // خطأ في الطلب
    return new Error(error.message || 'حدث خطأ غير متوقع');
  }
};

// ============================================================
// 4. واجهة برمجة التطبيقات (API)
// ============================================================

export const procuremindAPI = {
  // ============================================================
  // 💬 المحادثة (Chat)
  // ============================================================
  
  chat: {
    /**
     * 💬 إرسال سؤال
     * @param {string} question - سؤال المستخدم
     * @param {Object} options - خيارات إضافية
     * @returns {Promise} الرد مع المصادر
     */
    send: async (question, options = {}) => {
      const data = {
        question,
        session_id: options.sessionId || localStorage.getItem('session_id'),
        max_sources: options.maxSources || 5,
        temperature: options.temperature || 0.7,
        include_sources: options.includeSources !== false,
        filter_category: options.filterCategory || null,
        filter_supplier: options.filterSupplier || null,
      };
      
      const response = await post(ENDPOINTS.chat.send, data);
      return response;
    },
    
    /**
     * 🌊 إرسال سؤال مع تدفق
     * @param {string} question - سؤال المستخدم
     * @param {Function} onChunk - دالة استقبال الأجزاء
     * @param {Object} options - خيارات إضافية
     */
    stream: async (question, onChunk, options = {}) => {
      const data = {
        question,
        session_id: options.sessionId || localStorage.getItem('session_id'),
        max_sources: options.maxSources || 5,
        temperature: options.temperature || 0.7,
        include_sources: options.includeSources !== false,
      };
      
      try {
        const response = await fetch(`${BASE_URL}${ENDPOINTS.chat.stream}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
        
        if (!response.ok) {
          throw new Error('فشل في الاتصال بالخادم');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                onChunk({ done: true });
                return;
              }
              onChunk({ data, done: false });
            }
          }
        }
      } catch (error) {
        throw handleError(error);
      }
    },
    
    /**
     * 📜 جلب سجل المحادثة
     * @param {string} sessionId - معرف الجلسة
     * @returns {Promise} سجل المحادثة
     */
    getHistory: async (sessionId) => {
      return await get(ENDPOINTS.chat.history(sessionId));
    },
    
    /**
     * 🗑️ حذف سجل المحادثة
     * @param {string} sessionId - معرف الجلسة
     * @returns {Promise} نتيجة الحذف
     */
    clearHistory: async (sessionId) => {
      return await del(ENDPOINTS.chat.clearHistory(sessionId));
    },
    
    /**
     * 💡 الحصول على أسئلة مقترحة
     * @returns {Promise} قائمة الأسئلة المقترحة
     */
    getSuggestions: async () => {
      return await get(ENDPOINTS.chat.suggestions);
    },
  },

  // ============================================================
  // 📄 المستندات (Documents)
  // ============================================================
  
  documents: {
    /**
     * 📋 قائمة جميع المستندات
     * @param {Object} params - معلمات التصفية
     * @returns {Promise} قائمة المستندات
     */
    list: async (params = {}) => {
      return await get(ENDPOINTS.documents.list, params);
    },
    
    /**
     * 📤 رفع مستند جديد
     * @param {File} file - الملف
     * @param {Object} metadata - بيانات وصفية
     * @param {Function} onProgress - دالة تقدم الرفع
     * @returns {Promise} نتيجة الرفع
     */
    upload: async (file, metadata = {}, onProgress) => {
      const data = {
        category: metadata.category || 'other',
        description: metadata.description || '',
      };
      
      return await upload(ENDPOINTS.documents.upload, file, data, onProgress);
    },
    
    /**
     * 📄 الحصول على معلومات مستند
     * @param {string} docId - معرف المستند
     * @returns {Promise} معلومات المستند
     */
    get: async (docId) => {
      return await get(ENDPOINTS.documents.get(docId));
    },
    
    /**
     * 🗑️ حذف مستند
     * @param {string} docId - معرف المستند
     * @returns {Promise} نتيجة الحذف
     */
    delete: async (docId) => {
      return await del(ENDPOINTS.documents.delete(docId));
    },
    
    /**
     * ⬇️ تحميل مستند
     * @param {string} docId - معرف المستند
     * @returns {string} رابط التحميل
     */
    downloadUrl: (docId) => {
      return `${BASE_URL}${ENDPOINTS.documents.download(docId)}`;
    },
    
    /**
     * 🏷️ جلب جميع التصنيفات
     * @returns {Promise} التصنيفات
     */
    getCategories: async () => {
      return await get(ENDPOINTS.documents.categories);
    },
    
    /**
     * 🔄 إعادة بناء الفهرس
     * @returns {Promise} نتيجة إعادة البناء
     */
    reindex: async () => {
      return await post(ENDPOINTS.documents.reindex);
    },
  },

  // ============================================================
  // 🏢 الموردين (Suppliers)
  // ============================================================
  
  suppliers: {
    /**
     * 📋 قائمة جميع الموردين
     * @param {Object} params - معلمات التصفية
     * @returns {Promise} قائمة الموردين
     */
    list: async (params = {}) => {
      return await get(ENDPOINTS.suppliers.list, params);
    },
    
    /**
     * 📄 الحصول على معلومات مورد
     * @param {string} supplierId - معرف المورد
     * @returns {Promise} معلومات المورد
     */
    get: async (supplierId) => {
      return await get(ENDPOINTS.suppliers.get(supplierId));
    },
    
    /**
     * ➕ إضافة مورد جديد
     * @param {Object} data - بيانات المورد
     * @returns {Promise} نتيجة الإضافة
     */
    create: async (data) => {
      return await post(ENDPOINTS.suppliers.create, data);
    },
    
    /**
     * ✏️ تحديث معلومات مورد
     * @param {string} supplierId - معرف المورد
     * @param {Object} data - البيانات الجديدة
     * @returns {Promise} نتيجة التحديث
     */
    update: async (supplierId, data) => {
      return await put(ENDPOINTS.suppliers.update(supplierId), data);
    },
    
    /**
     * 🗑️ حذف مورد
     * @param {string} supplierId - معرف المورد
     * @returns {Promise} نتيجة الحذف
     */
    delete: async (supplierId) => {
      return await del(ENDPOINTS.suppliers.delete(supplierId));
    },
  },

  // ============================================================
  // 🔍 البحث (Search)
  // ============================================================
  
  search: {
    /**
     * 🔍 البحث الدلالي
     * @param {string} query - نص البحث
     * @param {Object} options - خيارات البحث
     * @returns {Promise} نتائج البحث
     */
    semantic: async (query, options = {}) => {
      const data = {
        query,
        category: options.category || null,
        supplier: options.supplier || null,
        top_k: options.topK || 10,
        min_score: options.minScore || 0.3,
      };
      return await post(ENDPOINTS.search.semantic, data);
    },
    
    /**
     * 🔍 البحث بالكلمات المفتاحية
     * @param {string} query - نص البحث
     * @param {Object} options - خيارات البحث
     * @returns {Promise} نتائج البحث
     */
    keywords: async (query, options = {}) => {
      const data = {
        query,
        category: options.category || null,
        supplier: options.supplier || null,
        top_k: options.topK || 10,
      };
      return await post(ENDPOINTS.search.keywords, data);
    },
    
    /**
     * 🔍 البحث الهجين
     * @param {string} query - نص البحث
     * @param {Object} options - خيارات البحث
     * @returns {Promise} نتائج البحث
     */
    hybrid: async (query, options = {}) => {
      const data = {
        query,
        category: options.category || null,
        supplier: options.supplier || null,
        top_k: options.topK || 10,
        semantic_weight: options.semanticWeight || 0.7,
        keyword_weight: options.keywordWeight || 0.3,
      };
      return await post(ENDPOINTS.search.hybrid, data);
    },
  },

  // ============================================================
  // 🩺 الصحة (Health)
  // ============================================================
  
  health: {
    /**
     * 🩺 فحص صحة النظام
     * @returns {Promise} حالة النظام
     */
    check: async () => {
      return await get(ENDPOINTS.health.check);
    },
    
    /**
     * 🔄 فحص جاهزية النظام
     * @returns {Promise} جاهزية النظام
     */
    readiness: async () => {
      return await get(ENDPOINTS.health.readiness);
    },
    
    /**
     * 💓 فحص أن الخادم يعمل
     * @returns {Promise} حالة الخادم
     */
    liveness: async () => {
      return await get(ENDPOINTS.health.liveness);
    },
  },

  // ============================================================
  // 📊 التحليلات (Analytics)
  // ============================================================
  
  analytics: {
    /**
     * 📊 الحصول على إحصائيات النظام
     * @returns {Promise} إحصائيات النظام
     */
    getStats: async () => {
      return await get(ENDPOINTS.analytics.stats);
    },
    
    /**
     * 📈 الحصول على إحصائيات الموردين
     * @returns {Promise} إحصائيات الموردين
     */
    getSuppliersStats: async () => {
      return await get(ENDPOINTS.analytics.suppliers);
    },
    
    /**
     * 📉 الحصول على إحصائيات المستندات
     * @returns {Promise} إحصائيات المستندات
     */
    getDocumentsStats: async () => {
      return await get(ENDPOINTS.analytics.documents);
    },
  },

  // ============================================================
  // 🔐 المصادقة (Auth)
  // ============================================================
  
  auth: {
    /**
     * 🔐 تسجيل الدخول
     * @param {string} username - اسم المستخدم
     * @param {string} password - كلمة المرور
     * @returns {Promise} توكن المصادقة
     */
    login: async (username, password) => {
      const data = { username, password };
      const response = await post(ENDPOINTS.auth.login, data);
      
      // حفظ التوكن
      if (response.token) {
        localStorage.setItem('auth_token', response.token);
      }
      
      return response;
    },
    
    /**
     * 🔐 تسجيل الخروج
     * @returns {Promise} نتيجة تسجيل الخروج
     */
    logout: async () => {
      const response = await post(ENDPOINTS.auth.logout);
      
      // حذف التوكن
      localStorage.removeItem('auth_token');
      
      return response;
    },
    
    /**
     * 🔐 التحقق من التوكن
     * @returns {Promise} صحة التوكن
     */
    verify: async () => {
      return await get(ENDPOINTS.auth.verify);
    },
    
    /**
     * 🔐 الحصول على التوكن الحالي
     * @returns {string|null} التوكن أو null
     */
    getToken: () => {
      return localStorage.getItem('auth_token');
    },
    
    /**
     * 🔐 التحقق من وجود توكن
     * @returns {boolean} وجود توكن
     */
    isAuthenticated: () => {
      return !!localStorage.getItem('auth_token');
    },
  },

  // ============================================================
  // 🛠️ أدوات مساعدة
  // ============================================================
  
  utils: {
    /**
     * 🆔 إنشاء معرف جلسة جديد
     * @returns {string} معرف الجلسة
     */
    generateSessionId: () => {
      const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('session_id', sessionId);
      return sessionId;
    },
    
    /**
     * 🆔 الحصول على معرف الجلسة الحالي
     * @returns {string|null} معرف الجلسة
     */
    getSessionId: () => {
      let sessionId = localStorage.getItem('session_id');
      if (!sessionId) {
        sessionId = generateSessionId();
      }
      return sessionId;
    },
    
    /**
     * 🗑️ مسح معرف الجلسة
     */
    clearSessionId: () => {
      localStorage.removeItem('session_id');
    },
  },
};

// ============================================================
// 5. تصدير افتراضي
// ============================================================

export default procuremindAPI;
