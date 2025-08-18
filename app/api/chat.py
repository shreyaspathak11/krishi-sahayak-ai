"""
Core API endpoints for Krishi Sahayak AI
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
import json
import asyncio
import logging
from typing import AsyncGenerator

from app.models.api_models import ChatRequest, ChatResponse
from app.services.language_service import language_service
from app.services.agentic_core import get_response

logger = logging.getLogger(__name__)

router = APIRouter()

def get_krishi_agent():
    """Get the krishi agent from main module, avoiding circular imports."""
    import app.main
    return app.main.krishi_agent

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Simple chat endpoint with optional streaming support.
    """
    krishi_agent = get_krishi_agent()
    
    if krishi_agent is None:
        raise HTTPException(status_code=500, detail="AI agent not initialized")
    
    try:
        logger.info(f"Chat request: {request.message} (Language: {request.language})")
        
        # If streaming is requested, return SSE response
        if request.stream:
            return StreamingResponse(
                generate_chat_stream(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        ai_response = get_response(
            krishi_agent, 
            request.message,
            language_code=request.language,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            response=ai_response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        
        return ChatResponse(
            response=language_service.get_template(request.language, "error"),
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )


async def generate_chat_stream(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate streaming response for chat."""
    krishi_agent = get_krishi_agent()
    
    try:
        response = get_response(
            krishi_agent, 
            request.message,
            language_code=request.language,
            chat_history=request.chat_history
        )
        
        # Stream the response word by word
        words = response.split()
        
        for i, word in enumerate(words):
            chunk_data = {
                "type": "token",
                "content": word + " ",
                "session_id": request.session_id,
                "index": i,
                "done": False,
                "language": request.language
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
            await asyncio.sleep(0.05)
        
        # Send completion chunk
        completion_data = {
            "type": "completion",
            "content": "",
            "session_id": request.session_id,
            "index": len(words),
            "done": True,
            "language": request.language
        }
        yield f"data: {json.dumps(completion_data)}\n\n"
        
    except Exception as e:
        # Get error message in appropriate language
        error_message = language_service.get_template(request.language, "error")

        error_data = {
            "type": "error",
            "content": error_message,
            "session_id": request.session_id,
            "index": 0,
            "done": True,
            "language": request.language
        }
        yield f"data: {json.dumps(error_data)}\n\n"
