# backend/app/models/__init__.py
"""
📦 وحدة النماذج - Models Module

تحتوي على جميع نماذج البيانات (Pydantic Schemas) المستخدمة في التطبيق
"""

from .schemas import (
    # نماذج الطلبات
    ChatRequest,
    DocumentUploadRequest,
    DocumentFilterRequest,
    SearchRequest,
    
    # نماذج الاستجابات
    ChatResponse,
    DocumentResponse,
    DocumentListResponse,
    HealthResponse,
    ErrorResponse,
    
    # نماذج البيانات
    Source,
    Message,
    Conversation,
    DocumentInfo,
    CategoryInfo,
    StatsInfo
)

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    # نماذج الطلبات
    'ChatRequest',
    'DocumentUploadRequest',
    'DocumentFilterRequest',
    'SearchRequest',
    
    # نماذج الاستجابات
    'ChatResponse',
    'DocumentResponse',
    'DocumentListResponse',
    'HealthResponse',
    'ErrorResponse',
    
    # نماذج البيانات
    'Source',
    'Message',
    'Conversation',
    'DocumentInfo',
    'CategoryInfo',
    'StatsInfo'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI Models Module - نماذج البيانات"

# أنواع النماذج
MODEL_TYPES = {
    "requests": "نماذج الطلبات (Request Schemas)",
    "responses": "نماذج الاستجابات (Response Schemas)",
    "data": "نماذج البيانات (Data Models)"
}
