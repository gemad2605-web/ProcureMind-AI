# backend/app/api/documents.py
"""
📄 إدارة المستندات - رفع، حذف، تحديث، عرض
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path

# استيراد الإعدادات والخدمات
from app.core.config import settings
from app.utils.logger import logger
from app.database.text_loader import TextLoader
from app.database.docx_loader import DocxLoader
from app.utils.file_utils import FileUtils

# إنشاء Router
router = APIRouter()

# ============================================================
# نماذج البيانات
# ============================================================

from pydantic import BaseModel, Field

class DocumentInfo(BaseModel):
    """
    معلومات المستند
    """
    id: str
    filename: str
    category: str
    path: str
    size: int
    uploaded_at: str
    last_modified: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentUploadResponse(BaseModel):
    """
    استجابة رفع المستند
    """
    success: bool
    message: str
    document: Optional[DocumentInfo] = None
    error: Optional[str] = None

class DocumentListResponse(BaseModel):
    """
    قائمة المستندات
    """
    documents: List[DocumentInfo]
    total: int
    timestamp: str

# ============================================================
# نقاط النهاية
# ============================================================

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    📋 قائمة جميع المستندات في قاعدة المعرفة
    
    **المعلمات:**
    - `category`: تصفية حسب التصنيف (contracts, policies, quotations, quality_reports)
    - `search`: بحث في أسماء الملفات
    - `limit`: عدد النتائج لكل صفحة
    - `offset`: بداية النتائج
    """
    
    logger.info(f"📋 جلب قائمة المستندات - category={category}, search={search}")
    
    try:
        # جلب المستندات
        documents = await FileUtils.get_documents(
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب المستندات: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في جلب المستندات: {str(e)}"
        )

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="الملف المراد رفعه"),
    category: str = Form(..., description="تصنيف المستند"),
    description: Optional[str] = Form(None, description="وصف المستند")
):
    """
    📤 رفع مستند جديد إلى قاعدة المعرفة
    
    **الملفات المدعومة:**
    - `.txt` - ملفات نصية
    - `.docx` - مستندات Word
    
    **التصنيفات المتاحة:**
    - `contracts` - عقود
    - `policies` - سياسات
    - `quotations` - عروض أسعار
    - `quality_reports` - تقارير الجودة
    - `other` - أخرى
    """
    
    logger.info(f"📤 رفع مستند جديد: {file.filename}")
    
    try:
        # 1. التحقق من نوع الملف
        allowed_extensions = ['.txt', '.docx']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return DocumentUploadResponse(
                success=False,
                message="نوع الملف غير مدعوم",
                error=f"الملفات المدعومة: {', '.join(allowed_extensions)}"
            )
        
        # 2. التحقق من التصنيف
        valid_categories = ['contracts', 'policies', 'quotations', 'quality_reports', 'other']
        if category not in valid_categories:
            return DocumentUploadResponse(
                success=False,
                message="تصنيف غير صحيح",
                error=f"التصنيفات المتاحة: {', '.join(valid_categories)}"
            )
        
        # 3. إنشاء معرف فريد للملف
        file_id = str(uuid.uuid4())[:8]
        new_filename = f"{file_id}_{file.filename}"
        
        # 4. تحديد مسار الحفظ
        upload_dir = settings.KNOWLEDGE_BASE_PATH / category
        os.makedirs(upload_dir, exist_ok=True)
        file_path = upload_dir / new_filename
        
        # 5. حفظ الملف
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 6. قراءة محتوى الملف
        content = None
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == '.docx':
            content = DocxLoader.extract_text(file_path)
        
        # 7. إضافة إلى الفهرس (إذا كان ناجحاً)
        if content:
            from app.database.faiss_loader import FAISSLoader
            faiss_loader = FAISSLoader()
            await faiss_loader.add_document(
                doc_id=file_id,
                content=content,
                metadata={
                    "filename": new_filename,
                    "category": category,
                    "original_name": file.filename,
                    "uploaded_at": datetime.now().isoformat(),
                    "description": description
                }
            )
        
        # 8. بناء معلومات المستند
        doc_info = DocumentInfo(
            id=file_id,
            filename=new_filename,
            category=category,
            path=str(file_path),
            size=os.path.getsize(file_path),
            uploaded_at=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            status="uploaded",
            metadata={
                "original_name": file.filename,
                "description": description,
                "content_length": len(content) if content else 0
            }
        )
        
        logger.info(f"✅ تم رفع المستند بنجاح: {new_filename}")
        
        return DocumentUploadResponse(
            success=True,
            message=f"تم رفع المستند بنجاح: {file.filename}",
            document=doc_info
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ في رفع المستند: {str(e)}")
        return DocumentUploadResponse(
            success=False,
            message="فشل رفع المستند",
            error=str(e)
        )

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    🗑️ حذف مستند من قاعدة المعرفة
    """
    
    logger.info(f"🗑️ حذف مستند: {doc_id}")
    
    try:
        # 1. البحث عن المستند
        doc_info = await FileUtils.get_document_by_id(doc_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"المستند {doc_id} غير موجود"
            )
        
        # 2. حذف الملف من النظام
        file_path = Path(doc_info.path)
        if file_path.exists():
            os.remove(file_path)
        
        # 3. حذف من الفهرس
        from app.database.faiss_loader import FAISSLoader
        faiss_loader = FAISSLoader()
        await faiss_loader.delete_document(doc_id)
        
        logger.info(f"✅ تم حذف المستند بنجاح: {doc_id}")
        
        return {
            "success": True,
            "message": f"تم حذف المستند بنجاح: {doc_info.filename}",
            "doc_id": doc_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ خطأ في حذف المستند: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في حذف المستند: {str(e)}"
        )

@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str):
    """
    ⬇️ تحميل مستند من قاعدة المعرفة
    """
    
    try:
        # البحث عن المستند
        doc_info = await FileUtils.get_document_by_id(doc_id)
        if not doc_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"المستند {doc_id} غير موجود"
            )
        
        # التحقق من وجود الملف
        file_path = Path(doc_info.path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="الملف غير موجود على الخادم"
            )
        
        # إرجاع الملف
        return FileResponse(
            path=file_path,
            filename=doc_info.filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل المستند: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في تحميل المستند: {str(e)}"
        )

@router.get("/documents/categories")
async def get_categories():
    """
    🏷️ جلب جميع التصنيفات المتاحة
    """
    
    categories = {
        "contracts": {
            "name": "عقود",
            "icon": "📄",
            "count": await FileUtils.count_documents_by_category("contracts"),
            "description": "عقود التوريد والموردين"
        },
        "policies": {
            "name": "سياسات",
            "icon": "📋",
            "count": await FileUtils.count_documents_by_category("policies"),
            "description": "سياسات وإجراءات العمل"
        },
        "quotations": {
            "name": "عروض أسعار",
            "icon": "💰",
            "count": await FileUtils.count_documents_by_category("quotations"),
            "description": "عروض أسعار من الموردين"
        },
        "quality_reports": {
            "name": "تقارير جودة",
            "icon": "⭐",
            "count": await FileUtils.count_documents_by_category("quality_reports"),
            "description": "تقارير تقييم الجودة للموردين"
        },
        "other": {
            "name": "أخرى",
            "icon": "📁",
            "count": await FileUtils.count_documents_by_category("other"),
            "description": "ملفات أخرى"
        }
    }
    
    return {
        "categories": categories,
        "total": sum(cat["count"] for cat in categories.values()),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/documents/reindex")
async def reindex_documents():
    """
    🔄 إعادة بناء فهرس FAISS من جميع المستندات
    """
    
    logger.info("🔄 جاري إعادة بناء الفهرس...")
    
    try:
        from app.database.faiss_loader import FAISSLoader
        from app.database.text_loader import TextLoader
        
        # 1. تحميل جميع النصوص
        text_loader = TextLoader()
        documents = await text_loader.load_all_documents()
        
        # 2. إعادة بناء الفهرس
        faiss_loader = FAISSLoader()
        await faiss_loader.rebuild_index(documents)
        
        logger.info(f"✅ تم إعادة بناء الفهرس مع {len(documents)} مستند")
        
        return {
            "success": True,
            "message": f"✅ تم إعادة بناء الفهرس مع {len(documents)} مستند",
            "doc_count": len(documents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة بناء الفهرس: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ في إعادة بناء الفهرس: {str(e)}"
        )
