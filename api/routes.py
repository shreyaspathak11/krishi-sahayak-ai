"""
API routes for Krishi Sahayak AI
"""

from fastapi import APIRouter

from .core import router as core_router
from .chat import router as chat_router
from .language import router as language_router
from .voice import router as voice_router

# Create main router instance
router = APIRouter()

# Include all sub-routers
router.include_router(core_router, tags=["core"])
router.include_router(chat_router, prefix="/api", tags=["chat"])
router.include_router(language_router, prefix="/api", tags=["language"])
router.include_router(voice_router, prefix="/api/voice", tags=["voice"])
