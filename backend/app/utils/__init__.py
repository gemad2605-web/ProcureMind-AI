# backend/app/utils/__init__.py
"""
🛠️ وحدة الأدوات المساعدة - Utils Module

تحتوي على أدوات ووظائف مساعدة تستخدم في جميع أنحاء التطبيق
"""

from .logger import logger, setup_logging
from .file_utils import (
    FileUtils,
    get_file_extension,
    is_file_allowed,
    read_text_file,
    write_text_file,
    get_file_size,
    get_file_info,
    create_directory,
    delete_file,
    get_file_hash,
    get_available_space,
    validate_file_path
)
from .helpers import (
    format_date,
    format_number,
    format_currency,
    clean_text,
    extract_keywords,
    truncate_text,
    safe_json_loads,
    safe_json_dumps,
    generate_id,
    generate_session_id,
    get_timestamp,
    is_valid_uuid,
    is_valid_email,
    calculate_similarity
)
from .validators import (
    validate_question,
    validate_file,
    validate_document_name,
    validate_supplier_name,
    validate_price,
    validate_rating
)

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    # التسجيل
    'logger',
    'setup_logging',
    
    # أدوات الملفات
    'FileUtils',
    'get_file_extension',
    'is_file_allowed',
    'read_text_file',
    'write_text_file',
    'get_file_size',
    'get_file_info',
    'create_directory',
    'delete_file',
    'get_file_hash',
    'get_available_space',
    'validate_file_path',
    
    # أدوات مساعدة
    'format_date',
    'format_number',
    'format_currency',
    'clean_text',
    'extract_keywords',
    'truncate_text',
    'safe_json_loads',
    'safe_json_dumps',
    'generate_id',
    'generate_session_id',
    'get_timestamp',
    'is_valid_uuid',
    'is_valid_email',
    'calculate_similarity',
    
    # التحقق من الصحة
    'validate_question',
    'validate_file',
    'validate_document_name',
    'validate_supplier_name',
    'validate_price',
    'validate_rating'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI Utils Module - أدوات ووظائف مساعدة"

# قائمة الأدوات المتاحة
UTILS_LIST = {
    "logger": "نظام التسجيل وإدارة السجلات",
    "file_utils": "أدوات التعامل مع الملفات",
    "helpers": "وظائف مساعدة عامة",
    "validators": "وظائف التحقق من صحة البيانات"
}
