"""
Pydantic models for Krishi Sahayak API
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


class ToolCall(BaseModel):
    """Information about a tool that was called."""
    name: str
    description: str
    input: Dict[str, Any]
    output: str
    status: str = "success"  # success, pending, error


class ChatResponse(BaseModel):
    """Standard chat response model with tool tracking."""
    response: str  # Final answer to show user
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = []  # Tools that were used
    thinking_process: Optional[str] = None  # Intermediate reasoning (optional)
    sources: Optional[List[str]] = []  # Data sources used


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
