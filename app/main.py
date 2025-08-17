# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.services.agentic_core import create_krishi_agent
from app.api import router
from app.config import Config

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- INITIALIZATION ---
app = FastAPI(
    title="Krishi Sahayak AI API",
    description="AI-powered agricultural assistant for Indian farmers",
    version="2.0.0"
)

# Add CORS middleware with production-ready settings
if Config.ALLOWED_ORIGINS == "*":
    # For wildcard origins, we can't use credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # For specific origins, we can use credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(router)

# Global variable for the AI agent (simple and effective)
krishi_agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent on startup."""
    global krishi_agent
    
    try:
        logger.info("Starting Krishi Sahayak AI API...")
        logger.info(f"Environment: {Config.ENVIRONMENT}")
        logger.info(f"Host: {Config.HOST}:{Config.PORT}")
        
        # Check if required environment variables are set
        if not Config.GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set! AI agent cannot be initialized.")
            krishi_agent = None
            return
        
        # Create and store the agent in global variable (simple!)
        krishi_agent = create_krishi_agent()
        
        logger.info("Krishi Sahayak AI API started successfully!")
        logger.info("Ready to serve farmers!")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.error("AI agent initialization failed, but API will continue to run")
        krishi_agent = None
        # Don't raise the exception - let the API start without the agent