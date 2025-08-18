"""
Language support API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict

from app.services.language_service import language_service

router = APIRouter()


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for the AI assistant.
    """
    return {
        "supported_languages": language_service.get_supported_languages(),
        "default_language": "en",
        "auto_detection_available": True
    }


@router.post("/detect-language")
async def detect_language(request: Dict[str, str]):
    """
    Detect language from input text.
    """
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    detected_language = language_service.detect_language(text)
    language_name = language_service.supported_languages.get(detected_language, "Unknown")

    return {
        "detected_language": detected_language,
        "language_name": language_name,
        "confidence": "high" if detected_language != "en" else "medium"  # Simple confidence
    }
