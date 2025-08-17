"""
Basic API endpoints (health check, root, etc.)
"""

from fastapi import APIRouter
from datetime import datetime

from app.models.api_models import HealthResponse

router = APIRouter()


@router.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Krishi Sahayak AI - Your Digital Farming Assistant",
        "version": "2.0.0",
        "description": "AI-powered agricultural assistant for Indian farmers",
        "endpoints": {
            "chat": "/api/chat - Unified chat with streaming support",
            "health": "/health - Health check",
            "docs": "/docs - API documentation"
        },
        "status": "ready"
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Krishi Sahayak AI API",
        timestamp=datetime.now().isoformat(),
        version="2.0.0"
    )
