# backend/app/api/chat.py
"""
💬 نقطة نهاية المحادثة - استقبال الأسئلة والرد عليها
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# استيراد الخدمات
from app.services.chat_service import ChatService
from app.core.config import settings
from app.utils.logger import logger

# إنشاء Router
router = APIRouter()

# ============================================================
# نماذج البيانات (Pydantic Schemas)
# ============================================================

class ChatRequest(BaseModel):
    """
    نموذج طلب المحادثة
    """
    question: str = Field(
        ...,
        description="سؤال المستخدم",
        min_length=1,
        max_length=1000,
        example="ما هي شروط عقد Alpha Inc؟"
    )
    session_id: Optional[str] = Field(
        None,
        description="معرف جلسة المحادثة"
    )
    max_sources: Optional[int] = Field(
        5,
        description="الحد الأقصى لعدد المصادر",
        ge=1,
        le=10
    )
    temperature: Optional[float] = Field(
        0.7,
        description="درجة الإبداع في الرد",
        ge=0.0,
        le=1.0
    )
    include_sources: Optional[bool] = Field(
        True,
        description="عرض المصادر مع الرد"
    )
    filter_category: Optional[str] = Field(
        None,
        description="تصفية حسب التصنيف (contracts, policies, quotations, quality_reports)"
    )
    filter_supplier: Optional[str] = Field(
        None,
        description="تصفية حسب اسم المورد"
    )

class Source(BaseModel):
    """
    نموذج المصدر
    """
    id: str
    filename: str
    category: str
    content: str
    relevance_score: float
    supplier: Optional[str] = None
    contract_value: Optional[float] = None
    quality_score: Optional[float] = None
    date_added: Optional[str] = None

class ChatResponse(BaseModel):
    """
    نموذج استجابة المحادثة
    """
    answer: str = Field(
        ...,
        description="الرد على سؤال المستخدم"
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="قائمة المصادر المستخدمة في الرد"
    )
    session_id: str = Field(
        ...,
        description="معرف جلسة المحادثة"
    )
    question_id: str = Field(
        ...,
        description="معرف السؤال"
    )
    timestamp: str = Field(
        ...,
        description="وقت الرد"
    )
    confidence_score: Optional[float] = Field(
        None,
        description="درجة الثقة في الإجابة (0-1)"
    )
    processing_time: Optional[float] = Field(
        None,
        description="زمن المعالجة بالثواني"
    )
    total_documents: Optional[int] = Field(
        None,
        description="إجمالي المستندات في قاعدة المعرفة"
    )
    retrieved_count: Optional[int] = Field(
        None,
        description="عدد المستندات المسترجعة"
    )

class ErrorResponse(BaseModel):
    """
    نموذج استجابة الخطأ
    """
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str

# ============================================================
# نقاط النهاية (Endpoints)
# ============================================================

# إنشاء خدمة المحادثة (Singleton)
chat_service = ChatService()

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"description": "تم الرد بنجاح"},
        400: {"description": "طلب غير صحيح"},
        404: {"description": "مصادر غير موجودة"},
        500: {"description": "خطأ في الخادم"}
    }
)
async def chat(request: ChatRequest):
    """
    🎯 نقطة النهاية الرئيسية للمحادثة
    
    تستقبل سؤال المستخدم وترد عليه باستخدام:
    1. البحث الدلالي في قاعدة المعرفة (FAISS)
    2. إعادة ترتيب النتائج (Reranking)
    3. توليد الإجابة باستخدام Grok AI
    
    **مثال:**
    ```json
    {
        "question": "ما هي شروط عقد Alpha Inc؟",
        "max_sources": 5,
        "temperature": 0.7
    }
