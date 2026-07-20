# backend/app/main.py
"""
🚀 نقطة الدخول الرئيسية للتطبيق - Main Application Entry Point

تقوم بإنشاء وتكوين تطبيق FastAPI وتسجيل جميع المكونات
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from datetime import datetime

from app.api.routes import router
from app.core.config import settings
from app.core.exceptions import ProcureMindException
from app.utils.logger import logger, setup_logging


# ============================================================
# 1. إدارة دورة حياة التطبيق
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق (بدء وإيقاف)
    """
    # 🚀 بدء التشغيل
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    logger.info("=" * 60)
    
    # تهيئة المكونات عند بدء التشغيل
    await startup_events()
    
    yield  # هنا يعمل التطبيق
    
    # 🛑 إيقاف التشغيل
    await shutdown_events()
    logger.info("👋 Application shutdown complete")


async def startup_events():
    """الأحداث التي تحدث عند بدء التشغيل"""
    try:
        # التحقق من وجود المجلدات
        from app.core.config import settings
        from pathlib import Path
        
        directories = [
            settings.KNOWLEDGE_BASE_PATH,
            settings.FAISS_INDEX_PATH,
            settings.DATA_PATH,
            settings.LOGS_PATH
        ]
        
        for dir_path in directories:
            if not dir_path.exists():
                logger.info(f"📁 Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # التحقق من وجود FAISS
        try:
            from app.database.faiss_loader import FAISSLoader
            loader = FAISSLoader()
            if loader.is_loaded:
                logger.info(f"✅ FAISS index loaded: {loader.get_index_size()} documents")
            else:
                logger.warning("⚠️ FAISS index not loaded - run build_index.py first")
        except Exception as e:
            logger.warning(f"⚠️ FAISS initialization warning: {str(e)}")
        
        # التحقق من LLM
        try:
            from app.llm.grok_client import GrokClient
            client = GrokClient()
            if client.api_key:
                logger.info("✅ Grok API key configured")
            else:
                logger.warning("⚠️ Grok API key not set in .env file")
        except Exception as e:
            logger.warning(f"⚠️ LLM initialization warning: {str(e)}")
        
        logger.info("✅ Startup events completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup events failed: {str(e)}")


async def shutdown_events():
    """الأحداث التي تحدث عند إيقاف التشغيل"""
    logger.info("🛑 Shutting down application...")
    # تنظيف الموارد إذا لزم الأمر
    logger.info("✅ Shutdown events completed")


# ============================================================
# 2. إنشاء التطبيق
# ============================================================

# إنشاء تطبيق FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=f"""
    🧠 {settings.APP_NAME} - نظام ذكاء اصطناعي للمشتريات
    
    **الميزات:**
    - 💬 محادثة ذكية مع المستندات
    - 🔍 بحث دلالي في العقود والوثائق
    - 📄 إدارة المستندات
    - 🏢 إدارة الموردين
    
    **التقنيات المستخدمة:**
    - RAG (Retrieval-Augmented Generation)
    - FAISS للبحث المتجهي
    - Grok AI من xAI
    """,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)


# ============================================================
# 3. إعدادات CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 4. معالجة الأخطاء (Exception Handlers)
# ============================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """معالجة أخطاء HTTP"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": str(exc.detail),
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """معالجة أخطاء التحقق من الصحة"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "بيانات غير صحيحة",
            "details": exc.errors(),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(ProcureMindException)
async def procuremind_exception_handler(request: Request, exc: ProcureMindException):
    """معالجة أخطاء التطبيق المخصصة"""
    logger.error(f"ProcureMind error: {str(exc)}")
    return JSONResponse(
        status_code=exc.status_code if hasattr(exc, 'status_code') else 400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """معالجة الأخطاء العامة"""
    logger.exception(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================
# 5. تسجيل المسارات (Routes)
# ============================================================

# تسجيل جميع المسارات من ملف routes.py
app.include_router(router)


# ============================================================
# 6. مسارات إضافية
# ============================================================

@app.get("/")
async def root():
    """
    🏠 نقطة البداية
    """
    return {
        "message": f"🚀 Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "online",
        "docs": "/docs" if settings.DEBUG else None,
        "endpoints": {
            "/api/chat": "POST - اسأل سؤالاً",
            "/api/health": "GET - فحص صحة النظام",
            "/api/documents": "GET - قائمة المستندات",
            "/api/documents/upload": "POST - رفع مستند"
        }
    }


@app.get("/api/health")
async def health_check():
    """
    🩺 فحص صحة النظام (مبسط)
    """
    from app.database.faiss_loader import FAISSLoader
    from app.llm.grok_client import GrokClient
    
    # فحص FAISS
    faiss_status = "healthy"
    faiss_message = "✅ FAISS is working"
    try:
        loader = FAISSLoader()
        if not loader.is_loaded:
            faiss_status = "warning"
            faiss_message = "⚠️ FAISS not loaded"
    except Exception as e:
        faiss_status = "error"
        faiss_message = f"❌ FAISS error: {str(e)}"
    
    # فحص LLM
    llm_status = "healthy"
    llm_message = "✅ LLM is configured"
    try:
        client = GrokClient()
        if not client.api_key:
            llm_status = "warning"
            llm_message = "⚠️ Grok API key not set"
    except Exception as e:
        llm_status = "error"
        llm_message = f"❌ LLM error: {str(e)}"
    
    return {
        "status": "healthy" if faiss_status == "healthy" and llm_status != "error" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "faiss": {
                "status": faiss_status,
                "message": faiss_message
            },
            "llm": {
                "status": llm_status,
                "message": llm_message,
                "model": settings.GROK_MODEL
            },
            "knowledge_base": {
                "status": "healthy" if settings.KNOWLEDGE_BASE_PATH.exists() else "warning",
                "path": str(settings.KNOWLEDGE_BASE_PATH)
            }
        }
    }


# ============================================================
# 7. تشغيل التطبيق
# ============================================================

if __name__ == "__main__":
    """
    تشغيل التطبيق مباشرة
    """
    # إعداد التسجيل
    setup_logging()
    
    # تشغيل الخادم
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1,
        log_level=settings.LOG_LEVEL.lower()
    )
