# backend/app/llm/llm_factory.py
"""
🏭 مصنع النماذج اللغوية (LLM Factory)

يقوم بإنشاء وإدارة العملاء المناسبين للنماذج اللغوية المختلفة
"""

from typing import Optional, Dict, Any, Type
from enum import Enum
from dataclasses import dataclass, field

from app.core.config import settings
from app.utils.logger import logger


class LLMProvider(str, Enum):
    """
    مزودو النماذج اللغوية المدعومة
    """
    GROK = "grok"
    OPENAI = "openai"
    LOCAL = "local"
    MOCK = "mock"  # للاختبار


@dataclass
class LLMConfig:
    """
    إعدادات النموذج اللغوي
    """
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 60
    extra_params: Dict[str, Any] = field(default_factory=dict)


class LLMFactory:
    """
    مصنع النماذج اللغوية
    
    يدعم:
    - إنشاء عملاء لنماذج مختلفة
    - التبديل بين النماذج بسهولة
    - إدارة إعدادات كل نموذج
    - التخزين المؤقت للعملاء
    """
    
    # مخزن العملاء (تخزين مؤقت)
    _clients = {}
    
    # الإعدادات الافتراضية لكل مزود
    DEFAULT_CONFIGS = {
        LLMProvider.GROK: {
            "model": "grok-1",
            "api_url": "https://api.x.ai/v1/chat/completions",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        LLMProvider.OPENAI: {
            "model": "gpt-4",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        LLMProvider.LOCAL: {
            "model": "llama-2",
            "api_url": "http://localhost:11434/api/generate",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        LLMProvider.MOCK: {
            "model": "mock",
            "api_url": "",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    def __init__(self):
        """تهيئة المصنع"""
        self.default_provider = LLMProvider.GROK
        self.current_provider = self.default_provider
        self.configs = self._load_configs()
        
        logger.info(f"🏭 LLM Factory initialized with default: {self.default_provider}")
    
    # ============================================================
    # الطريقة الرئيسية - إنشاء عميل
    # ============================================================
    
    def get_client(
        self,
        provider: Optional[LLMProvider] = None,
        config: Optional[LLMConfig] = None,
        use_cache: bool = True
    ):
        """
        الحصول على عميل النموذج اللغوي
        
        Args:
            provider: مزود النموذج
            config: إعدادات مخصصة
            use_cache: استخدام التخزين المؤقت
            
        Returns:
            عميل النموذج اللغوي
        """
        # تحديد المزود
        provider = provider or self.current_provider
        
        # إنشاء مفتاح التخزين المؤقت
        cache_key = self._get_cache_key(provider, config)
        
        # التحقق من التخزين المؤقت
        if use_cache and cache_key in self._clients:
            logger.debug(f"📦 Returning cached client for {provider}")
            return self._clients[cache_key]
        
        # إنشاء عميل جديد
        client = self._create_client(provider, config)
        
        # تخزين في التخزين المؤقت
        if use_cache:
            self._clients[cache_key] = client
        
        logger.info(f"✅ Created client for {provider}")
        
        return client
    
    def get_default_client(self, use_cache: bool = True):
        """
        الحصول على العميل الافتراضي
        
        Args:
            use_cache: استخدام التخزين المؤقت
            
        Returns:
            العميل الافتراضي
        """
        return self.get_client(
            provider=self.default_provider,
            use_cache=use_cache
        )
    
    def switch_provider(
        self,
        provider: LLMProvider,
        config: Optional[LLMConfig] = None
    ) -> None:
        """
        التبديل إلى مزود آخر
        
        Args:
            provider: المزود الجديد
            config: إعدادات مخصصة
        """
        self.current_provider = provider
        if config:
            self._update_config(provider, config)
        
        logger.info(f"🔄 Switched to provider: {provider}")
    
    # ============================================================
    # طرق إنشاء العملاء
    # ============================================================
    
    def _create_client(self, provider: LLMProvider, config: Optional[LLMConfig] = None):
        """
        إنشاء عميل للنموذج اللغوي
        
        Args:
            provider: مزود النموذج
            config: إعدادات مخصصة
            
        Returns:
            عميل النموذج اللغوي
        """
        # الحصول على الإعدادات
        config = self._merge_config(provider, config)
        
        # إنشاء العميل حسب المزود
        if provider == LLMProvider.GROK:
            return self._create_grok_client(config)
        elif provider == LLMProvider.OPENAI:
            return self._create_openai_client(config)
        elif provider == LLMProvider.LOCAL:
            return self._create_local_client(config)
        elif provider == LLMProvider.MOCK:
            return self._create_mock_client(config)
        else:
            raise ValueError(f"❌ Unsupported provider: {provider}")
    
    def _create_grok_client(self, config: LLMConfig):
        """
        إنشاء عميل Grok
        
        Args:
            config: إعدادات Grok
            
        Returns:
            عميل Grok
        """
        from app.llm.grok_client import GrokClient
        
        return GrokClient(
            api_key=config.api_key or settings.GROK_API_KEY,
            api_url=config.api_url,
            model=config.model,
            timeout=config.timeout
        )
    
    def _create_openai_client(self, config: LLMConfig):
        """
        إنشاء عميل OpenAI
        
        Args:
            config: إعدادات OpenAI
            
        Returns:
            عميل OpenAI
        """
        try:
            from openai import AsyncOpenAI
            
            return AsyncOpenAI(
                api_key=config.api_key or settings.OPENAI_API_KEY,
                base_url=config.api_url,
                timeout=config.timeout
            )
        except ImportError:
            logger.warning("⚠️ OpenAI package not installed")
            return self._create_mock_client(config)
        except Exception as e:
            logger.error(f"❌ Error creating OpenAI client: {e}")
            return self._create_mock_client(config)
    
    def _create_local_client(self, config: LLMConfig):
        """
        إنشاء عميل للنموذج المحلي
        
        Args:
            config: إعدادات النموذج المحلي
            
        Returns:
            عميل النموذج المحلي
        """
        try:
            # محاولة استيراد عميل Ollama (مثال)
            from app.llm.local_client import LocalLLMClient
            
            return LocalLLMClient(
                api_url=config.api_url,
                model=config.model,
                timeout=config.timeout
            )
        except ImportError:
            logger.warning("⚠️ Local LLM client not available")
            return self._create_mock_client(config)
        except Exception as e:
            logger.error(f"❌ Error creating local client: {e}")
            return self._create_mock_client(config)
    
    def _create_mock_client(self, config: LLMConfig):
        """
        إنشاء عميل وهمي (للاختبار)
        
        Args:
            config: إعدادات وهمية
            
        Returns:
            عميل وهمي
        """
        from app.llm.mock_client import MockLLMClient
        
        return MockLLMClient(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
    
    # ============================================================
    # طرق إدارة الإعدادات
    # ============================================================
    
    def _load_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        تحميل إعدادات النماذج من الإعدادات العامة
        
        Returns:
            إعدادات النماذج
        """
        configs = {}
        
        # Grok
        configs[LLMProvider.GROK.value] = {
            "model": settings.GROK_MODEL,
            "api_url": settings.GROK_API_URL,
            "api_key": settings.GROK_API_KEY
        }
        
        # OpenAI (إذا كانت الإعدادات موجودة)
        if hasattr(settings, 'OPENAI_API_KEY'):
            configs[LLMProvider.OPENAI.value] = {
                "model": getattr(settings, 'OPENAI_MODEL', 'gpt-4'),
                "api_url": getattr(settings, 'OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions'),
                "api_key": settings.OPENAI_API_KEY
            }
        
        # إعدادات إضافية
        configs.update(self._load_custom_configs())
        
        return configs
    
    def _load_custom_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        تحميل إعدادات مخصصة من ملفات خارجية
        
        Returns:
            إعدادات مخصصة
        """
        custom_configs = {}
        
        # محاولة تحميل من ملف config.json
        try:
            import json
            from pathlib import Path
            
            config_path = Path("config/llm_config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key in ["grok", "openai", "local"]:
                            custom_configs[key] = value
        except Exception as e:
            logger.debug(f"📝 No custom LLM config found: {e}")
        
        return custom_configs
    
    def _merge_config(
        self,
        provider: LLMProvider,
        config: Optional[LLMConfig] = None
    ) -> LLMConfig:
        """
        دمج الإعدادات مع القيم الافتراضية
        
        Args:
            provider: مزود النموذج
            config: إعدادات مخصصة
            
        Returns:
            الإعدادات المدمجة
        """
        # الإعدادات الافتراضية
        default = self.DEFAULT_CONFIGS.get(provider, {})
        
        # الإعدادات من الملفات
        provider_config = self.configs.get(provider.value, {})
        
        # دمج الإعدادات
        merged = {
            "provider": provider,
            "model": config.model if config else default.get("model", ""),
            "api_key": (
                config.api_key if config and config.api_key
                else provider_config.get("api_key")
            ),
            "api_url": (
                config.api_url if config and config.api_url
                else provider_config.get("api_url", default.get("api_url", ""))
            ),
            "temperature": (
                config.temperature if config
                else default.get("temperature", 0.7)
            ),
            "max_tokens": (
                config.max_tokens if config
                else default.get("max_tokens", 1000)
            ),
            "timeout": (
                config.timeout if config
                else default.get("timeout", 60)
            ),
            "extra_params": {}
        }
        
        return LLMConfig(**merged)
    
    def _update_config(self, provider: LLMProvider, config: LLMConfig) -> None:
        """
        تحديث إعدادات مزود معين
        
        Args:
            provider: مزود النموذج
            config: الإعدادات الجديدة
        """
        self.configs[provider.value] = {
            "model": config.model,
            "api_url": config.api_url,
            "api_key": config.api_key
        }
        
        logger.info(f"📝 Updated config for {provider}")
    
    def _get_cache_key(
        self,
        provider: LLMProvider,
        config: Optional[LLMConfig] = None
    ) -> str:
        """
        إنشاء مفتاح للتخزين المؤقت
        
        Args:
            provider: مزود النموذج
            config: إعدادات مخصصة
            
        Returns:
            مفتاح التخزين المؤقت
        """
        if config:
            return f"{provider.value}_{config.model}_{config.temperature}"
        return provider.value
    
    # ============================================================
    # طرق إدارة العملاء
    # ============================================================
    
    def list_clients(self) -> Dict[str, str]:
        """
        قائمة العملاء المتاحة
        
        Returns:
            قائمة العملاء
        """
        return {
            provider.value: self.DEFAULT_CONFIGS.get(provider, {}).get("model", "unknown")
            for provider in LLMProvider
        }
    
    def clear_cache(self) -> None:
        """مسح التخزين المؤقت للعملاء"""
        self._clients.clear()
        logger.info("🗑️ Client cache cleared")
    
    def get_current_provider(self) -> str:
        """
        الحصول على المزود الحالي
        
        Returns:
            اسم المزود الحالي
        """
        return self.current_provider.value
    
    def is_available(self, provider: LLMProvider) -> bool:
        """
        التحقق من توفر مزود معين
        
        Args:
            provider: مزود النموذج
            
        Returns:
            توفر المزود
        """
        if provider == LLMProvider.MOCK:
            return True
        
        if provider == LLMProvider.GROK:
            return bool(settings.GROK_API_KEY)
        
        if provider == LLMProvider.OPENAI:
            return bool(getattr(settings, 'OPENAI_API_KEY', None))
        
        if provider == LLMProvider.LOCAL:
            # التحقق من وجود نموذج محلي
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
        
        return False
    
    def get_fallback_providers(self) -> List[LLMProvider]:
        """
        الحصول على قائمة المزودين الاحتياطيين
        
        Returns:
            قائمة المزودين الاحتياطيين
        """
        available = []
        
        for provider in LLMProvider:
            if self.is_available(provider) and provider != self.current_provider:
                available.append(provider)
        
        return available
    
    # ============================================================
    # طرق مساعدة
    # ============================================================
    
    def create_with_fallback(
        self,
        preferred_provider: Optional[LLMProvider] = None,
        fallback_providers: Optional[List[LLMProvider]] = None
    ):
        """
        إنشاء عميل مع الاحتياطي (إذا فشل المزود الأساسي)
        
        Args:
            preferred_provider: المزود المفضل
            fallback_providers: قائمة المزودين الاحتياطيين
            
        Returns:
            عميل النموذج اللغوي
        """
        providers = [preferred_provider or self.current_provider]
        
        if fallback_providers:
            providers.extend(fallback_providers)
        else:
            providers.extend(self.get_fallback_providers())
        
        for provider in providers:
            try:
                logger.info(f"🔄 Trying provider: {provider}")
                client = self.get_client(provider)
                
                # اختبار العميل
                if hasattr(client, 'check_health'):
                    is_healthy = client.check_health()
                    if is_healthy:
                        logger.info(f"✅ Provider {provider} is healthy")
                        return client
                else:
                    # إذا لم يكن هناك check_health، اعتبره صحيحاً
                    return client
                    
            except Exception as e:
                logger.warning(f"⚠️ Provider {provider} failed: {e}")
                continue
        
        # إذا فشل جميع المزودين، استخدم الـ Mock
        logger.warning("⚠️ All providers failed, using Mock client")
        return self.get_client(LLMProvider.MOCK)
