"""
Pydantic models for Krishi Sahayak AI API
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    """Unified chat request model with optional enhanced features."""
    message: str  # Changed from 'question' to 'message' for consistency
    farmer_context: Dict[str, Any] = {}
    chat_history: List[Dict[str, Any]] = []
    session_id: Optional[str] = None
    language: Optional[str] = "en"  # ISO 639-1 language code
    stream: Optional[bool] = False  # Whether to return streaming response


class ChatResponse(BaseModel):
    """Standard chat response model."""
    response: str
    timestamp: Optional[str] = None
    session_id: Optional[str] = None


class FarmerProfile(BaseModel):
    """Farmer profile data model."""
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    farm_size: Optional[str] = None
    crops: List[str] = []
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    farming_experience: Optional[str] = None
    primary_concerns: Optional[str] = None
    language: Optional[str] = "en"  # ISO 639-1 language code (en, hi, pa, bn, etc.)


class SessionInfo(BaseModel):
    """Session information model."""
    current_time: str
    local_date: str
    session_id: str


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    timestamp: str
    version: Optional[str] = None
    details: Optional[str] = None
