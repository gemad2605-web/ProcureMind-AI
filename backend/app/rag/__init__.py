# backend/app/rag/__init__.py
"""
🧠 وحدة RAG (Retrieval-Augmented Generation)

تحتوي على جميع مكونات نظام الاسترجاع والتوليد المدعوم بالاسترجاع
"""

from .retriever import Retriever
from .semantic_search import SemanticSearch
from .qa_engine import QAEngine
from .reranker import Reranker
from .chunking import Chunking

# تعريف ما يتم تصديره عند استيراد الوحدة
__all__ = [
    'Retriever',
    'SemanticSearch',
    'QAEngine',
    'Reranker',
    'Chunking'
]

# معلومات الوحدة
__version__ = "1.0.0"
__description__ = "ProcureMind-AI RAG Module - محرك الاسترجاع والتوليد"

# وصف المكونات
COMPONENTS = {
    "retriever": "استرجاع المستندات من FAISS",
    "semantic_search": "البحث الدلالي باستخدام المتجهات",
    "qa_engine": "محرك الأسئلة والأجوبة (RAG Pipeline)",
    "reranker": "إعادة ترتيب النتائج (Cross-Encoder)",
    "chunking": "تقسيم النصوص إلى أجزاء"
}
