# backend/app/database/__init__.py
"""
🗄️ وحدة قاعدة البيانات - Database Module

تحتوي على جميع مكونات التعامل مع قواعد البيانات والفهارس
"""

from .faiss_loader import FAISSLoader
from .embeddings import Embeddings
from .text_loader import TextLoader
from .docx_loader import DocxLoader
from .file_mapper import FileMapper

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    'FAISSLoader',
    'Embeddings',
    'TextLoader',
    'DocxLoader',
    'FileMapper'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI Database Module - إدارة قواعد البيانات والفهارس"

# وصف المكونات
COMPONENTS = {
    "faiss_loader": "تحميل وإدارة فهرس FAISS",
    "embeddings": "توليد المتجهات (Embeddings) للنصوص",
    "text_loader": "تحميل النصوص من ملفات .txt",
    "docx_loader": "تحميل النصوص من ملفات .docx",
    "file_mapper": "ربط الملفات بالفهارس والبيانات الوصفية"
}

# أنواع الملفات المدعومة
SUPPORTED_FILE_TYPES = {
    "txt": {
        "description": "ملفات نصية عادية",
        "loader": "TextLoader",
        "icon": "📄"
    },
    "docx": {
        "description": "مستندات Word",
        "loader": "DocxLoader",
        "icon": "📝"
    }
}

# إعدادات قاعدة البيانات
DATABASE_SETTINGS = {
    "faiss": {
        "index_path": "./faiss_index/index.faiss",
        "metadata_path": "./faiss_index/metadata.pkl",
        "dimension": 384,  # أبعاد المتجهات
        "metric": "L2"     # مقياس المسافة
    },
    "embeddings": {
        "model_name": "all-MiniLM-L6-v2",
        "device": "cpu",
        "batch_size": 32
    }
}
