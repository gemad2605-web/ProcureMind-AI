# backend/app/api/__init__.py
"""
📌 وحدة API - تحتوي على جميع نقاط النهاية (Endpoints)
"""

from .routes import router
from .chat import router as chat_router
from .health import router as health_router
from .documents import router as documents_router

__all__ = [
    'router',
    'chat_router',
    'health_router',
    'documents_router'
]
