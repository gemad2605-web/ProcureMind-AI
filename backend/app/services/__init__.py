# backend/app/services/__init__.py
"""
🔧 وحدة الخدمات - Services Module

تحتوي على جميع خدمات التطبيق (منطق الأعمال)
"""

from .chat_service import ChatService
from .document_service import DocumentService
from .supplier_service import SupplierService
from .search_service import SearchService

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    'ChatService',
    'DocumentService',
    'SupplierService',
    'SearchService'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI Services Module - منطق الأعمال"

# وصف الخدمات
SERVICES = {
    "chat_service": "خدمة المحادثة - إدارة RAG والرد على الأسئلة",
    "document_service": "خدمة المستندات - إدارة رفع وتحميل وحذف المستندات",
    "supplier_service": "خدمة الموردين - إدارة معلومات الموردين",
    "search_service": "خدمة البحث - البحث الدلالي والوصفي"
}

# إعدادات الخدمات
SERVICE_DEFAULTS = {
    "chat": {
        "max_history": 50,
        "default_temperature": 0.7,
        "default_top_k": 5
    },
    "document": {
        "max_file_size": 10485760,  # 10MB
        "allowed_extensions": [".txt", ".docx", ".pdf"]
    },
    "search": {
        "default_limit": 10,
        "min_score": 0.3
    }
}
