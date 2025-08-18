"""
Pydantic models for Krishi Sahayak AI API
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    """Simplified chat request model for frontend."""
    message: str  # The user's message
    chat_history: List[Dict[str, Any]] = []  # Conversation history from frontend
    session_id: Optional[str] = None  # To track conversation sessions
    language: Optional[str] = "en"  # ISO 639-1 language code
    stream: Optional[bool] = False  # Whether to return streaming response


class ChatResponse(BaseModel):
    """Standard chat response model."""
    response: str
    timestamp: Optional[str] = None
    session_id: Optional[str] = None


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
