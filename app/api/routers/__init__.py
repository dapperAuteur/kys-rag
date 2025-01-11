# app/api/routers/__init__.py

from .scientific_study import router as scientific_study_router
from .article import router as article_router
from .search import router as search_router
from .chat import router as chat_router
from .pdf import router as pdf_router

__all__ = [
    'scientific_study_router',
    'article_router',
    'search_router',
    'chat_router',
    'pdf_router'
]