# backend/app/llm/__init__.py
"""
🤖 وحدة LLM (Large Language Models)

تحتوي على جميع مكونات التواصل مع النماذج اللغوية الكبيرة
"""

from .grok_client import GrokClient
from .llm_factory import LLMFactory

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    'GrokClient',
    'LLMFactory'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI LLM Module - التواصل مع النماذج اللغوية"

# وصف المكونات
COMPONENTS = {
    "grok_client": "عميل Grok API من xAI",
    "llm_factory": "مصنع النماذج - اختيار النموذج المناسب"
}

# قائمة النماذج المدعومة
SUPPORTED_MODELS = {
    "grok": {
        "name": "Grok",
        "provider": "xAI",
        "default_model": "grok-1",
        "description": "نموذج Grok من xAI"
    },
    "openai": {
        "name": "OpenAI",
        "provider": "OpenAI",
        "default_model": "gpt-4",
        "description": "نموذج GPT من OpenAI"
    },
    "local": {
        "name": "Local",
        "provider": "Local",
        "default_model": "llama-2",
        "description": "نموذج محلي (Llama, Mistral, الخ)"
    }
}
