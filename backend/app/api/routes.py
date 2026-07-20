# backend/app/api/routes.py
"""
📌 تسجيل جميع المسارات (Routes) في التطبيق
"""

from fastapi import APIRouter
from .chat import router as chat_router
from .health import router as health_router
from .documents import router as documents_router

# إنشاء Router رئيسي
router = APIRouter()

# تسجيل جميع الـ Routers الفرعية
router.include_router(chat_router, prefix="/api", tags=["Chat"])
router.include_router(health_router, prefix="/api", tags=["Health"])
router.include_router(documents_router, prefix="/api", tags=["Documents"])


# ============================================================
# نقاط النهاية العامة
# ============================================================

@router.get("/")
async def root():
    """
    🏠 نقطة البداية - ترحيب
    """
    return {
        "message": "🚀 Welcome to ProcureMind-AI API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "chat": {
                "url": "/api/chat",
                "method": "POST",
                "description": "اسأل سؤالاً عن المستندات"
            },
            "chat_stream": {
                "url": "/api/chat/stream",
                "method": "POST",
                "description": "اسأل سؤالاً مع تدفق الرد"
            },
            "chat_history": {
                "url": "/api/chat/history/{session_id}",
                "method": "GET",
                "description": "جلب سجل المحادثة"
            },
            "chat_suggestions": {
                "url": "/api/chat/suggestions",
                "method": "GET",
                "description": "اقتراحات أسئلة"
            },
            "health": {
                "url": "/health",
                "method": "GET",
                "description": "فحص صحة النظام"
            },
            "health_readiness": {
                "url": "/health/readiness",
                "method": "GET",
                "description": "فحص جاهزية النظام"
            },
            "health_liveness": {
                "url": "/health/liveness",
                "method": "GET",
                "description": "فحص أن الخادم يعمل"
            },
            "documents": {
                "url": "/api/documents",
                "method": "GET",
                "description": "قائمة جميع المستندات"
            },
            "documents_upload": {
                "url": "/api/documents/upload",
                "method": "POST",
                "description": "رفع مستند جديد"
            },
            "documents_categories": {
                "url": "/api/documents/categories",
                "method": "GET",
                "description": "جلب تصنيفات المستندات"
            },
            "documents_reindex": {
                "url": "/api/documents/reindex",
                "method": "POST",
                "description": "إعادة بناء الفهرس"
            },
            "ping": {
                "url": "/api/ping",
                "method": "GET",
                "description": "اختبار الاتصال بالخادم"
            }
        },
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


@router.get("/api/ping")
async def ping():
    """
    🏓 اختبار الاتصال بالخادم
    """
    return {
        "status": "pong",
        "message": "✅ Server is alive!",
        "timestamp": "2026-07-20T00:00:00Z"
    }
