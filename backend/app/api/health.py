# backend/app/api/health.py
"""
🩺 نقطة نهاية للتحقق من صحة الخادم والمكونات
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import os
import sys
import platform

# استيراد الإعدادات
from app.core.config import settings
from app.utils.logger import logger

# إنشاء Router
router = APIRouter()


class HealthChecker:
    """
    فحص صحة المكونات
    """
    
    @staticmethod
    async def check_faiss() -> Dict[str, Any]:
        """فحص اتصال FAISS"""
        try:
            from app.database.faiss_loader import FAISSLoader
            loader = FAISSLoader()
            status = await loader.check_health()
            return {
                "status": "healthy" if status else "unhealthy",
                "message": "✅ FAISS is working" if status else "❌ FAISS is not working"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ FAISS error: {str(e)}"
            }
    
    @staticmethod
    async def check_llm() -> Dict[str, Any]:
        """فحص اتصال LLM (Grok)"""
        try:
            from app.llm.grok_client import GrokClient
            client = GrokClient()
            status = await client.check_health()
            return {
                "status": "healthy" if status else "unhealthy",
                "message": "✅ LLM is working" if status else "❌ LLM is not working"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ LLM error: {str(e)}"
            }
    
    @staticmethod
    async def check_knowledge_base() -> Dict[str, Any]:
        """فحص قاعدة المعرفة"""
        try:
            kb_path = settings.KNOWLEDGE_BASE_PATH
            if not os.path.exists(kb_path):
                return {
                    "status": "warning",
                    "message": "⚠️ Knowledge base path not found"
                }
            
            # حساب عدد الملفات
            doc_count = 0
            for root, dirs, files in os.walk(kb_path):
                doc_count += len([f for f in files if f.endswith(('.txt', '.docx', '.pdf'))])
            
            return {
                "status": "healthy",
                "message": f"✅ Knowledge base has {doc_count} documents",
                "doc_count": doc_count,
                "path": str(kb_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Knowledge base error: {str(e)}"
            }
    
    @staticmethod
    async def check_disk_space() -> Dict[str, Any]:
        """فحص المساحة على القرص"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (2**30)
            total_gb = total // (2**30)
            
            status = "healthy" if free_gb > 1 else "warning"
            return {
                "status": status,
                "message": f"{'✅' if status == 'healthy' else '⚠️'} Free space: {free_gb}GB / {total_gb}GB",
                "free_gb": free_gb,
                "total_gb": total_gb,
                "free_percent": round((free / total) * 100, 2)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Disk space check error: {str(e)}"
            }


# ============================================================
# نقاط النهاية
# ============================================================

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    🩺 فحص صحة النظام
    
    **المكونات التي يتم فحصها:**
    - ✅ FAISS (قاعدة البيانات المتجهية)
    - ✅ LLM (Grok API)
    - ✅ قاعدة المعرفة (المستندات)
    - ✅ مساحة القرص
    - ✅ حالة الخادم
    """
    
    logger.info("🩺 جاري فحص صحة النظام...")
    
    # فحص جميع المكونات
    faiss_status = await HealthChecker.check_faiss()
    llm_status = await HealthChecker.check_llm()
    kb_status = await HealthChecker.check_knowledge_base()
    disk_status = await HealthChecker.check_disk_space()
    
    # الحالة العامة
    all_healthy = all([
        faiss_status.get("status") == "healthy",
        llm_status.get("status") == "healthy",
        kb_status.get("status") in ["healthy", "warning"]
    ])
    
    # معلومات النظام
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "hostname": platform.node()
    }
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "faiss": faiss_status,
            "llm": llm_status,
            "knowledge_base": kb_status,
            "disk_space": disk_status
        },
        "system": system_info,
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "documents": "/api/documents",
            "docs": "/docs"
        }
    }


@router.get("/health/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    🔄 فحص جاهزية التطبيق لاستقبال الطلبات
    """
    
    # فحص سريع للمكونات الأساسية
    faiss_status = await HealthChecker.check_faiss()
    llm_status = await HealthChecker.check_llm()
    
    is_ready = (
        faiss_status.get("status") == "healthy" and
        llm_status.get("status") == "healthy"
    )
    
    return {
        "ready": is_ready,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "faiss": faiss_status.get("status"),
            "llm": llm_status.get("status")
        }
    }


@router.get("/health/liveness")
async def liveness_check():
    """
    💓 فحص أن الخادم لا يزال يعمل
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }
