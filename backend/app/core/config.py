# backend/app/core/config.py
"""
⚙️ إعدادات التطبيق - Application Configuration

يقرأ الإعدادات من ملف .env ويوفرها للتطبيق
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()


class Settings:
    """
    إعدادات التطبيق
    
    يتم قراءة جميع الإعدادات من متغيرات البيئة
    """
    
    # ============================================================
    # 🔑 مفاتيح API
    # ============================================================
    
    # Grok API (xAI)
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-1")
    GROK_API_URL: str = os.getenv(
        "GROK_API_URL",
        "https://api.x.ai/v1/chat/completions"
    )
    
    # OpenAI API (اختياري - احتياطي)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_API_URL: str = os.getenv(
        "OPENAI_API_URL",
        "https://api.openai.com/v1/chat/completions"
    )
    
    # ============================================================
    # 📁 مسارات الملفات
    # ============================================================
    
    # المسار الأساسي للمشروع
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    
    # مجلدات التطبيق
    KNOWLEDGE_BASE_PATH: Path = Path(
        os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    )
    FAISS_INDEX_PATH: Path = Path(
        os.getenv("FAISS_INDEX_PATH", "./faiss_index")
    )
    DATA_PATH: Path = Path(
        os.getenv("DATA_PATH", "./data")
    )
    LOGS_PATH: Path = Path(
        os.getenv("LOGS_PATH", "./logs")
    )
    
    # ============================================================
    # 🧬 إعدادات المتجهات (Embeddings)
    # ============================================================
    
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    
    # ============================================================
    # 📊 إعدادات RAG
    # ============================================================
    
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "10"))
    DEFAULT_MAX_SOURCES: int = int(os.getenv("DEFAULT_MAX_SOURCES", "5"))
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    MIN_CONFIDENCE_SCORE: float = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.3"))
    
    # إعدادات التقسيم (Chunking)
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    MIN_CHUNK_SIZE: int = int(os.getenv("MIN_CHUNK_SIZE", "50"))
    
    # ============================================================
    # 🗄️ إعدادات قاعدة البيانات
    # ============================================================
    
    # PostgreSQL (اختياري)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    
    # Redis (اختياري - للتخزين المؤقت)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))
    
    # ============================================================
    # 🖥️ إعدادات الخادم
    # ============================================================
    
    APP_NAME: str = os.getenv("APP_NAME", "ProcureMind-AI")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # خادم API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")
    
    # ============================================================
    # 📝 إعدادات التسجيل (Logging)
    # ============================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # ============================================================
    # 🔒 إعدادات الأمان
    # ============================================================
    
    # JWT (للمصادقة)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    # معدل الطلبات
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # ثانية
    
    # ============================================================
    # 📄 إعدادات المستندات
    # ============================================================
    
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = os.getenv(
        "ALLOWED_EXTENSIONS",
        ".txt,.docx,.pdf"
    ).split(",")
    
    # ============================================================
    # 🧪 إعدادات الاختبار
    # ============================================================
    
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def get_database_url(self) -> str:
        """
        الحصول على رابط قاعدة البيانات
        """
        if self.TESTING:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL
    
    def is_production(self) -> bool:
        """
        التحقق من أن البيئة إنتاجية
        """
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """
        التحقق من أن البيئة تطويرية
        """
        return self.ENVIRONMENT.lower() == "development"
    
    def is_testing(self) -> bool:
        """
        التحقق من أن البيئة اختبارية
        """
        return self.TESTING or self.ENVIRONMENT.lower() == "testing"
    
    def get_cors_origins(self) -> List[str]:
        """
        الحصول على قائمة CORS Origins
        """
        return self.CORS_ORIGINS
    
    def get_allowed_extensions(self) -> List[str]:
        """
        الحصول على قائمة الامتدادات المسموحة
        """
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS if ext.strip()]
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """
        الحصول على إعدادات المتجهات
        """
        return {
            "model_name": self.EMBEDDING_MODEL,
            "device": self.EMBEDDING_DEVICE,
            "batch_size": self.EMBEDDING_BATCH_SIZE,
            "dimension": self.EMBEDDING_DIMENSION
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """
        الحصول على إعدادات RAG
        """
        return {
            "top_k": self.DEFAULT_TOP_K,
            "max_sources": self.DEFAULT_MAX_SOURCES,
            "temperature": self.DEFAULT_TEMPERATURE,
            "min_confidence": self.MIN_CONFIDENCE_SCORE,
            "chunk_size": self.CHUNK_SIZE,
            "chunk_overlap": self.CHUNK_OVERLAP
        }
    
    def get_llm_config(self, provider: str = "grok") -> Dict[str, Any]:
        """
        الحصول على إعدادات النموذج اللغوي
        
        Args:
            provider: مزود النموذج (grok, openai)
        """
        if provider == "grok":
            return {
                "api_key": self.GROK_API_KEY,
                "model": self.GROK_MODEL,
                "api_url": self.GROK_API_URL
            }
        elif provider == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "api_url": self.OPENAI_API_URL
            }
        else:
            return {}
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        الحصول على إعدادات التسجيل
        """
        return {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "file": self.LOG_FILE,
            "max_size": self.LOG_MAX_SIZE,
            "backup_count": self.LOG_BACKUP_COUNT
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """
        الحصول على إعدادات الأمان
        """
        return {
            "secret_key": self.SECRET_KEY,
            "jwt_algorithm": self.JWT_ALGORITHM,
            "jwt_expire_minutes": self.JWT_EXPIRE_MINUTES,
            "rate_limit_requests": self.RATE_LIMIT_REQUESTS,
            "rate_limit_period": self.RATE_LIMIT_PERIOD
        }
    
    def get_paths(self) -> Dict[str, Path]:
        """
        الحصول على جميع مسارات الملفات
        """
        return {
            "base": self.BASE_DIR,
            "knowledge_base": self.KNOWLEDGE_BASE_PATH,
            "faiss_index": self.FAISS_INDEX_PATH,
            "data": self.DATA_PATH,
            "logs": self.LOGS_PATH
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل جميع الإعدادات إلى قاموس
        """
        return {
            # مفاتيح API
            "GROK_API_KEY": "***" if self.GROK_API_KEY else "",
            "GROK_MODEL": self.GROK_MODEL,
            "OPENAI_API_KEY": "***" if self.OPENAI_API_KEY else "",
            "OPENAI_MODEL": self.OPENAI_MODEL,
            
            # المسارات
            "KNOWLEDGE_BASE_PATH": str(self.KNOWLEDGE_BASE_PATH),
            "FAISS_INDEX_PATH": str(self.FAISS_INDEX_PATH),
            "DATA_PATH": str(self.DATA_PATH),
            "LOGS_PATH": str(self.LOGS_PATH),
            
            # إعدادات المتجهات
            "EMBEDDING_MODEL": self.EMBEDDING_MODEL,
            "EMBEDDING_DEVICE": self.EMBEDDING_DEVICE,
            "EMBEDDING_BATCH_SIZE": self.EMBEDDING_BATCH_SIZE,
            "EMBEDDING_DIMENSION": self.EMBEDDING_DIMENSION,
            
            # إعدادات RAG
            "DEFAULT_TOP_K": self.DEFAULT_TOP_K,
            "DEFAULT_MAX_SOURCES": self.DEFAULT_MAX_SOURCES,
            "DEFAULT_TEMPERATURE": self.DEFAULT_TEMPERATURE,
            "MIN_CONFIDENCE_SCORE": self.MIN_CONFIDENCE_SCORE,
            "CHUNK_SIZE": self.CHUNK_SIZE,
            "CHUNK_OVERLAP": self.CHUNK_OVERLAP,
            
            # إعدادات الخادم
            "APP_NAME": self.APP_NAME,
            "APP_VERSION": self.APP_VERSION,
            "ENVIRONMENT": self.ENVIRONMENT,
            "DEBUG": self.DEBUG,
            "API_HOST": self.API_HOST,
            "API_PORT": self.API_PORT,
            "API_PREFIX": self.API_PREFIX,
            
            # إعدادات الأمان
            "SECRET_KEY": "***" if self.SECRET_KEY else "",
            "JWT_ALGORITHM": self.JWT_ALGORITHM,
            "JWT_EXPIRE_MINUTES": self.JWT_EXPIRE_MINUTES,
            "RATE_LIMIT_REQUESTS": self.RATE_LIMIT_REQUESTS,
            "RATE_LIMIT_PERIOD": self.RATE_LIMIT_PERIOD,
            
            # إعدادات المستندات
            "MAX_FILE_SIZE": self.MAX_FILE_SIZE,
            "ALLOWED_EXTENSIONS": self.ALLOWED_EXTENSIONS,
            
            # إعدادات التسجيل
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FILE": self.LOG_FILE,
        }


# ============================================================
# إنشاء كائن الإعدادات
# ============================================================

settings = Settings()


# ============================================================
# التحقق من الإعدادات عند بدء التشغيل
# ============================================================

def validate_settings():
    """
    التحقق من صحة الإعدادات عند بدء التشغيل
    """
    # التحقق من وجود مفتاح Grok
    if not settings.GROK_API_KEY:
        print("⚠️ تحذير: GROK_API_KEY غير موجود في ملف .env")
        print("   يرجى إضافة المفتاح لتشغيل النموذج اللغوي")
    
    # التحقق من وجود مجلدات
    directories = [
        settings.KNOWLEDGE_BASE_PATH,
        settings.FAISS_INDEX_PATH,
        settings.DATA_PATH,
        settings.LOGS_PATH
    ]
    
    for dir_path in directories:
        if not dir_path.exists():
            print(f"📁 إنشاء مجلد: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # التحقق من بيئة التشغيل
    if settings.is_production():
        print("🚀 تشغيل في بيئة إنتاجية")
    elif settings.is_development():
        print("🛠️ تشغيل في بيئة تطويرية")
    elif settings.is_testing():
        print("🧪 تشغيل في بيئة اختبارية")
    
    print(f"📦 {settings.APP_NAME} v{settings.APP_VERSION}")


# تشغيل التحقق عند بدء التشغيل
validate_settings()
