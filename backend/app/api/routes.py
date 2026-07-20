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

# مسار الترحيب
@router.get("/")
async def root():
    """
    نقطة البداية - ترحيب
    """
    return {
        "message": "🚀 Welcome to ProcureMind-AI API",
        "version": "1.0.0",
        "endpoints": {
            "/api/chat": "POST - Ask a question",
            "/api/health": "GET - Check system health",
            "/api/documents": "GET - List all documents",
            "/api/documents/upload": "POST - Upload a document",
            "/api/documents/{doc_id}": "DELETE - Delete a document"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

# مسار لاختبار الاتصال
@router.get("/api/ping")
async def ping():
    """
    اختبار الاتصال بالخادم
    """
    return {"status": "pong", "message": "✅ Server is alive!"}
