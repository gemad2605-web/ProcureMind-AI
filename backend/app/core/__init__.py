# backend/app/core/__init__.py
"""
⚙️ وحدة النواة - Core Module

تحتوي على الإعدادات الأساسية والثوابت والتكوينات العامة للتطبيق
"""

from .config import settings
from .prompts import RAG_PROMPTS, SYSTEM_PROMPTS
from .constants import (
    APP_NAME,
    APP_VERSION,
    SUPPORTED_FILE_TYPES,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TOP_K,
    DEFAULT_MAX_SOURCES,
    DEFAULT_TEMPERATURE,
    MIN_CONFIDENCE_SCORE,
    CATEGORIES,
    FILE_EXTENSIONS
)
from .exceptions import (
    ProcureMindException,
    ConfigurationError,
    DocumentNotFoundError,
    IndexError,
    LLMError,
    ValidationError
)

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    # الإعدادات
    'settings',
    
    # النماذج التوجيهية
    'RAG_PROMPTS',
    'SYSTEM_PROMPTS',
    
    # الثوابت
    'APP_NAME',
    'APP_VERSION',
    'SUPPORTED_FILE_TYPES',
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_TOP_K',
    'DEFAULT_MAX_SOURCES',
    'DEFAULT_TEMPERATURE',
    'MIN_CONFIDENCE_SCORE',
    'CATEGORIES',
    'FILE_EXTENSIONS',
    
    # الاستثناءات
    'ProcureMindException',
    'ConfigurationError',
    'DocumentNotFoundError',
    'IndexError',
    'LLMError',
    'ValidationError'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI Core Module - الإعدادات الأساسية والثوابت"

# تعريف المكونات الأساسية
CORE_COMPONENTS = {
    "config": "إعدادات التطبيق من ملف .env",
    "prompts": "النماذج التوجيهية للنماذج اللغوية",
    "constants": "الثوابت والإعدادات الافتراضية",
    "exceptions": "استثناءات مخصصة للتطبيق"
}
