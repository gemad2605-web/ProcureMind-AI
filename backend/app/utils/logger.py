# backend/app/utils/logger.py
"""
📝 نظام التسجيل - Logging System

يوفر واجهة موحدة للتسجيل في جميع أنحاء التطبيق
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from app.core.config import settings


# ============================================================
# 1. إعدادات التسجيل
# ============================================================

# مستويات التسجيل
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# تنسيقات التسجيل
DEFAULT_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
DETAILED_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s'
JSON_FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'

# ألوان الطرفية
COLORS = {
    'DEBUG': '\033[94m',    # أزرق
    'INFO': '\033[92m',     # أخضر
    'WARNING': '\033[93m',  # أصفر
    'ERROR': '\033[91m',    # أحمر
    'CRITICAL': '\033[95m', # أرجواني
    'RESET': '\033[0m'      # إعادة تعيين
}


# ============================================================
# 2. تنسيقات مخصصة
# ============================================================

class ColoredFormatter(logging.Formatter):
    """
    تنسيق مع ألوان للطرفية
    """
    
    def format(self, record):
        # إضافة اللون حسب المستوى
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """
    تنسيق JSON للسجلات
    """
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # إضافة الاستثناءات إذا وجدت
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# ============================================================
# 3. إعدادات التسجيل الرئيسية
# ============================================================

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
    use_colors: bool = True,
    use_json: bool = False
) -> None:
    """
    إعداد نظام التسجيل
    
    Args:
        log_level: مستوى التسجيل
        log_file: مسار ملف السجل
        log_format: تنسيق السجل
        max_bytes: الحد الأقصى لحجم الملف
        backup_count: عدد النسخ الاحتياطية
        use_colors: استخدام الألوان
        use_json: استخدام تنسيق JSON
    """
    # إعدادات افتراضية
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE
    log_format = log_format or settings.LOG_FORMAT
    max_bytes = max_bytes or settings.LOG_MAX_SIZE
    backup_count = backup_count or settings.LOG_BACKUP_COUNT
    
    # تحويل مستوى التسجيل
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # إنشاء المجلد
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # إعداد المعالج الأساسي
    handlers = []
    
    # معالج الطرفية
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    elif use_colors:
        console_handler.setFormatter(ColoredFormatter(log_format))
    else:
        console_handler.setFormatter(logging.Formatter(log_format))
    
    handlers.append(console_handler)
    
    # معالج الملف
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # إعداد الجذر
    logging.basicConfig(
        level=level,
        handlers=handlers
    )
    
    # إعدادات إضافية
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # تسجيل بدء التشغيل
    logger = logging.getLogger("ProcureMind")
    logger.info("🚀 Logging system initialized")
    logger.info(f"📊 Log level: {log_level}")
    logger.info(f"📁 Log file: {log_file}")


# ============================================================
# 4. إنشاء كائن المسجل
# ============================================================

def get_logger(name: str = "ProcureMind") -> logging.Logger:
    """
    الحصول على مسجل باسم محدد
    
    Args:
        name: اسم المسجل
        
    Returns:
        كائن المسجل
    """
    return logging.getLogger(name)


# ============================================================
# 5. واجهة برمجة التطبيقات
# ============================================================

class Logger:
    """
    واجهة برمجة التطبيقات للتسجيل
    
    توفر واجهة سهلة الاستخدام للتسجيل في جميع أنحاء التطبيق
    """
    
    def __init__(self, name: str = "ProcureMind"):
        self.logger = get_logger(name)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة DEBUG"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة INFO"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة WARNING"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة ERROR"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة CRITICAL"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """تسجيل استثناء"""
        self.logger.exception(message, *args, **kwargs)
    
    def log(self, level: str, message: str, *args, **kwargs) -> None:
        """تسجيل رسالة بمستوى محدد"""
        level = level.upper()
        if level == 'DEBUG':
            self.debug(message, *args, **kwargs)
        elif level == 'INFO':
            self.info(message, *args, **kwargs)
        elif level == 'WARNING':
            self.warning(message, *args, **kwargs)
        elif level == 'ERROR':
            self.error(message, *args, **kwargs)
        elif level == 'CRITICAL':
            self.critical(message, *args, **kwargs)
        else:
            self.info(message, *args, **kwargs)


# ============================================================
# 6. دوال مساعدة إضافية
# ============================================================

def log_function_call(func):
    """
    ديكوراتور لتسجيل استدعاءات الدوال
    
    Args:
        func: الدالة المراد تسجيلها
        
    Returns:
        الدالة المزودة بالتسجيل
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"🔹 Calling {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ {func.__name__} failed: {str(e)}")
            raise
    
    return wrapper


def log_async_function_call(func):
    """
    ديكوراتور لتسجيل استدعاءات الدوال غير المتزامنة
    
    Args:
        func: الدالة المراد تسجيلها
        
    Returns:
        الدالة المزودة بالتسجيل
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"🔹 Calling async {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"✅ {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ {func.__name__} failed: {str(e)}")
            raise
    
    return wrapper


def log_exception(exc: Exception, context: Optional[str] = None) -> None:
    """
    تسجيل استثناء مع سياق إضافي
    
    Args:
        exc: الاستثناء
        context: السياق الإضافي
    """
    logger = get_logger()
    if context:
        logger.error(f"❌ Exception in {context}: {str(exc)}")
    else:
        logger.error(f"❌ Exception: {str(exc)}")
    logger.exception(exc)


# ============================================================
# 7. تهيئة التسجيل تلقائياً
# ============================================================

# إعداد التسجيل عند استيراد الوحدة
if not logging.getLogger().handlers:
    setup_logging()


# ============================================================
# 8. إنشاء كائن المسجل الرئيسي
# ============================================================

logger = Logger()

# تصدير الدوال الرئيسية
__all__ = [
    'logger',
    'Logger',
    'setup_logging',
    'get_logger',
    'log_function_call',
    'log_async_function_call',
    'log_exception',
    'LOG_LEVELS'
]
