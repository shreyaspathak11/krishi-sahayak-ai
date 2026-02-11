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
        "message": "Krishi Sahayak - Your Digital Farming Assistant",
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
    """Health check endpoint - responds immediately even during agent loading."""
    from app.main import krishi_agent, agent_loading
    
    if agent_loading:
        # Agent is still initializing - but server IS healthy and running
        return HealthResponse(
            status="healthy",
            service="Krishi Sahayak API",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            details="AI agent is initializing... API is ready."
        )
    
    if krishi_agent is None:
        return HealthResponse(
            status="unhealthy",
            service="Krishi Sahayak API",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            details="AI agent not initialized"
        )
    
    # Agent is loaded - report healthy without running a test query
    # (test queries in health checks are expensive and slow on Render)
    return HealthResponse(
        status="healthy",
        service="Krishi Sahayak API",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        details="AI agent is ready"
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
        "service": "Krishi Sahayak API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "message": "API is running"
    }
