# backend/app/models/schemas.py
"""
📦 نماذج البيانات (Pydantic Schemas)

تحتوي على جميع نماذج البيانات المستخدمة في الطلبات والاستجابات
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================
# 1. التعدادات (Enums)
# ============================================================

class DocumentCategory(str, Enum):
    """تصنيفات المستندات"""
    CONTRACTS = "contracts"
    POLICIES = "policies"
    QUOTATIONS = "quotations"
    QUALITY_REPORTS = "quality_reports"
    INVOICES = "invoices"
    PURCHASE_ORDERS = "purchase_orders"
    MANUALS = "manuals"
    REPORTS = "reports"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """حالة المستند"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class MessageRole(str, Enum):
    """دور المرسل في المحادثة"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RelevanceLabel(str, Enum):
    """تسمية درجة الأهمية"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============================================================
# 2. نماذج الطلبات (Request Schemas)
# ============================================================

class ChatRequest(BaseModel):
    """
    طلب المحادثة
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
        description="تصفية حسب التصنيف"
    )
    filter_supplier: Optional[str] = Field(
        None,
        description="تصفية حسب اسم المورد"
    )
    
    @validator('question')
    def validate_question(cls, v):
        if not v or v.strip() == "":
            raise ValueError("السؤال لا يمكن أن يكون فارغاً")
        return v.strip()


class DocumentUploadRequest(BaseModel):
    """
    طلب رفع مستند
    """
    filename: str = Field(
        ...,
        description="اسم الملف",
        example="contract_001.docx"
    )
    category: DocumentCategory = Field(
        ...,
        description="تصنيف المستند"
    )
    description: Optional[str] = Field(
        None,
        description="وصف المستند"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="علامات للمستند"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="بيانات وصفية إضافية"
    )


class DocumentFilterRequest(BaseModel):
    """
    طلب تصفية المستندات
    """
    category: Optional[DocumentCategory] = Field(
        None,
        description="تصنيف المستند"
    )
    search: Optional[str] = Field(
        None,
        description="بحث في أسماء الملفات"
    )
    supplier: Optional[str] = Field(
        None,
        description="اسم المورد"
    )
    date_from: Optional[datetime] = Field(
        None,
        description="من تاريخ"
    )
    date_to: Optional[datetime] = Field(
        None,
        description="إلى تاريخ"
    )
    status: Optional[DocumentStatus] = Field(
        None,
        description="حالة المستند"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="علامات"
    )
    limit: Optional[int] = Field(
        50,
        description="عدد النتائج لكل صفحة",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        0,
        description="بداية النتائج",
        ge=0
    )


class SearchRequest(BaseModel):
    """
    طلب البحث
    """
    query: str = Field(
        ...,
        description="نص البحث",
        min_length=1,
        max_length=500
    )
    category: Optional[DocumentCategory] = Field(
        None,
        description="تصفية حسب التصنيف"
    )
    supplier: Optional[str] = Field(
        None,
        description="تصفية حسب المورد"
    )
    top_k: Optional[int] = Field(
        10,
        description="عدد النتائج",
        ge=1,
        le=50
    )
    min_score: Optional[float] = Field(
        0.3,
        description="الحد الأدنى للدرجة",
        ge=0.0,
        le=1.0
    )


# ============================================================
# 3. نماذج البيانات (Data Models)
# ============================================================

class Source(BaseModel):
    """
    مصدر المستند
    """
    id: str = Field(
        ...,
        description="معرف المصدر"
    )
    filename: str = Field(
        ...,
        description="اسم الملف"
    )
    category: str = Field(
        ...,
        description="تصنيف المستند"
    )
    content: str = Field(
        ...,
        description="نص المستند"
    )
    relevance_score: float = Field(
        ...,
        description="درجة المطابقة",
        ge=0.0,
        le=1.0
    )
    preview: Optional[str] = Field(
        None,
        description="معاينة النص"
    )
    supplier: Optional[str] = Field(
        None,
        description="اسم المورد"
    )
    contract_value: Optional[float] = Field(
        None,
        description="قيمة العقد"
    )
    quality_score: Optional[float] = Field(
        None,
        description="درجة الجودة"
    )
    date_added: Optional[str] = Field(
        None,
        description="تاريخ الإضافة"
    )


class Message(BaseModel):
    """
    رسالة في المحادثة
    """
    id: str = Field(
        ...,
        description="معرف الرسالة"
    )
    role: MessageRole = Field(
        ...,
        description="دور المرسل"
    )
    content: str = Field(
        ...,
        description="محتوى الرسالة"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="وقت الرسالة"
    )
    sources: Optional[List[Source]] = Field(
        None,
        description="المصادر المستخدمة"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="بيانات وصفية إضافية"
    )


class Conversation(BaseModel):
    """
    محادثة كاملة
    """
    id: str = Field(
        ...,
        description="معرف المحادثة"
    )
    session_id: str = Field(
        ...,
        description="معرف الجلسة"
    )
    messages: List[Message] = Field(
        default_factory=list,
        description="قائمة الرسائل"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="تاريخ الإنشاء"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="تاريخ التحديث"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="بيانات وصفية"
    )


class DocumentInfo(BaseModel):
    """
    معلومات المستند
    """
    id: str = Field(
        ...,
        description="معرف المستند"
    )
    filename: str = Field(
        ...,
        description="اسم الملف"
    )
    category: str = Field(
        ...,
        description="تصنيف المستند"
    )
    path: str = Field(
        ...,
        description="مسار الملف"
    )
    size: int = Field(
        ...,
        description="حجم الملف بالبايت"
    )
    uploaded_at: str = Field(
        ...,
        description="تاريخ الرفع"
    )
    last_modified: str = Field(
        ...,
        description="تاريخ التعديل"
    )
    status: DocumentStatus = Field(
        ...,
        description="حالة المستند"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="بيانات وصفية إضافية"
    )
    content_preview: Optional[str] = Field(
        None,
        description="معاينة المحتوى"
    )


class CategoryInfo(BaseModel):
    """
    معلومات التصنيف
    """
    name: str = Field(
        ...,
        description="اسم التصنيف"
    )
    display_name: str = Field(
        ...,
        description="الاسم المعروض"
    )
    icon: str = Field(
        ...,
        description="أيقونة التصنيف"
    )
    count: int = Field(
        ...,
        description="عدد المستندات في التصنيف"
    )
    description: Optional[str] = Field(
        None,
        description="وصف التصنيف"
    )


class StatsInfo(BaseModel):
    """
    إحصائيات النظام
    """
    total_documents: int = Field(
        ...,
        description="إجمالي المستندات"
    )
    total_suppliers: int = Field(
        ...,
        description="إجمالي الموردين"
    )
    total_contracts: int = Field(
        ...,
        description="إجمالي العقود"
    )
    average_quality_score: float = Field(
        ...,
        description="متوسط درجة الجودة"
    )
    categories: Dict[str, int] = Field(
        ...,
        description="المستندات حسب التصنيف"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="آخر تحديث"
    )


# ============================================================
# 4. نماذج الاستجابات (Response Schemas)
# ============================================================

class ChatResponse(BaseModel):
    """
    استجابة المحادثة
    """
    answer: str = Field(
        ...,
        description="الرد على سؤال المستخدم"
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="قائمة المصادر المستخدمة"
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
        description="درجة الثقة في الإجابة (0-1)",
        ge=0.0,
        le=1.0
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


class DocumentResponse(BaseModel):
    """
    استجابة مستند
    """
    success: bool = Field(
        ...,
        description="نجاح العملية"
    )
    message: str = Field(
        ...,
        description="رسالة الحالة"
    )
    document: Optional[DocumentInfo] = Field(
        None,
        description="معلومات المستند"
    )
    error: Optional[str] = Field(
        None,
        description="رسالة الخطأ"
    )


class DocumentListResponse(BaseModel):
    """
    استجابة قائمة المستندات
    """
    documents: List[DocumentInfo] = Field(
        ...,
        description="قائمة المستندات"
    )
    total: int = Field(
        ...,
        description="إجمالي عدد المستندات"
    )
    offset: Optional[int] = Field(
        0,
        description="بداية النتائج"
    )
    limit: Optional[int] = Field(
        50,
        description="عدد النتائج"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="وقت الاستجابة"
    )


class HealthResponse(BaseModel):
    """
    استجابة فحص الصحة
    """
    status: str = Field(
        ...,
        description="حالة النظام (healthy/unhealthy)"
    )
    timestamp: str = Field(
        ...,
        description="وقت الفحص"
    )
    version: str = Field(
        ...,
        description="إصدار التطبيق"
    )
    environment: str = Field(
        ...,
        description="بيئة التشغيل"
    )
    components: Dict[str, Any] = Field(
        ...,
        description="حالة المكونات"
    )
    system: Dict[str, Any] = Field(
        ...,
        description="معلومات النظام"
    )
    endpoints: Dict[str, str] = Field(
        ...,
        description="نقاط النهاية المتاحة"
    )


class ErrorResponse(BaseModel):
    """
    استجابة الخطأ
    """
    error: str = Field(
        ...,
        description="نوع الخطأ"
    )
    message: str = Field(
        ...,
        description="رسالة الخطأ"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="تفاصيل إضافية"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="وقت الخطأ"
    )
    status_code: int = Field(
        ...,
        description="رمز حالة HTTP"
    )


class SuggestionsResponse(BaseModel):
    """
    استجابة الأسئلة المقترحة
    """
    suggestions: List[Dict[str, Any]] = Field(
        ...,
        description="قائمة الأسئلة المقترحة"
    )
    count: int = Field(
        ...,
        description="عدد الأسئلة"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="وقت الاستجابة"
    )


class CategoryListResponse(BaseModel):
    """
    استجابة قائمة التصنيفات
    """
    categories: Dict[str, CategoryInfo] = Field(
        ...,
        description="التصنيفات"
    )
    total: int = Field(
        ...,
        description="إجمالي المستندات"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="وقت الاستجابة"
    )


# ============================================================
# 5. نماذج مساعدة
# ============================================================

class PaginationParams(BaseModel):
    """
    معلمات التصفية والترتيب
    """
    page: int = Field(
        1,
        description="رقم الصفحة",
        ge=1
    )
    page_size: int = Field(
        20,
        description="حجم الصفحة",
        ge=1,
        le=100
    )
    sort_by: Optional[str] = Field(
        None,
        description="حقل الترتيب"
    )
    sort_order: Optional[str] = Field(
        "asc",
        description="ترتيب تصاعدي/تنازلي",
        pattern="^(asc|desc)$"
    )


class UploadResponse(BaseModel):
    """
    استجابة رفع الملف
    """
    success: bool = Field(
        ...,
        description="نجاح الرفع"
    )
    message: str = Field(
        ...,
        description="رسالة الحالة"
    )
    file_id: Optional[str] = Field(
        None,
        description="معرف الملف"
    )
    file_name: Optional[str] = Field(
        None,
        description="اسم الملف"
    )
    file_size: Optional[int] = Field(
        None,
        description="حجم الملف"
    )
    error: Optional[str] = Field(
        None,
        description="رسالة الخطأ"
    )


# ============================================================
# 6. نماذج الإعدادات
# ============================================================

class ModelConfig(BaseModel):
    """
    إعدادات النموذج
    """
    model_name: str = Field(
        ...,
        description="اسم النموذج"
    )
    temperature: float = Field(
        0.7,
        description="درجة الإبداع",
        ge=0.0,
        le=1.0
    )
    max_tokens: int = Field(
        1000,
        description="الحد الأقصى للرموز",
        ge=1,
        le=4000
    )
    top_p: float = Field(
        0.9,
        description="نواة العينة",
        ge=0.0,
        le=1.0
    )
    frequency_penalty: float = Field(
        0.0,
        description="عقوبة التكرار",
        ge=-2.0,
        le=2.0
    )
    presence_penalty: float = Field(
        0.0,
        description="عقوبة الحضور",
        ge=-2.0,
        le=2.0
    )
