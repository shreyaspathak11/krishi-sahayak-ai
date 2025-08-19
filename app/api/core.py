"""
Basic API endpoints (health check, root, etc.)
"""

from datetime import datetime
from fastapi import APIRouter, Response

from app.models import HealthResponse

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
    from app.main import krishi_agent
    
    # Check if the AI agent is properly initialized
    if krishi_agent is None:
        return HealthResponse(
            status="unhealthy",
            service="Krishi Sahayak AI API",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            details="AI agent not initialized"
        )
    
    try:
        # Test a simple query to ensure the agent is working
        test_response = krishi_agent.invoke({"input": "Hello", "chat_history": []})
        if test_response and 'output' in test_response:
            return HealthResponse(
                status="healthy",
                service="Krishi Sahayak AI API",
                timestamp=datetime.now().isoformat(),
                version="2.0.0",
                details="AI agent is working properly"
            )
        else:
            return HealthResponse(
                status="unhealthy",
                service="Krishi Sahayak AI API",
                timestamp=datetime.now().isoformat(),
                version="2.0.0",
                details="AI agent response format error"
            )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            service="Krishi Sahayak AI API",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            details=f"AI agent error: {str(e)}"
        )


@router.options("/{full_path:path}")
async def options_handler(full_path: str, response: Response):
    """Handle CORS preflight requests."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
    return {"message": "OK"}


@router.get("/status")
async def status_check():
    """Simple status check that doesn't require AI agent."""
    return {
        "status": "running",
        "service": "Krishi Sahayak AI API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "message": "API is running"
    }
