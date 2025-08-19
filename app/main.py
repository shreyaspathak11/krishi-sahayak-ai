# app/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from our organized modules
from app.config import Config
from app.services import create_krishi_agent
from app.api import router

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600 
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
        
        # Validate required environment variables
        try:
            Config.validate_required_env_vars()
            logger.info("✓ All required environment variables are set")
        except ValueError as e:
            logger.error(f"❌ Environment validation failed: {e}")
            krishi_agent = None
            return
        
        # Create and store the agent in global variable
        krishi_agent = create_krishi_agent()
        
        logger.info("✓ Krishi Sahayak AI API started successfully!")
        logger.info("🌾 Ready to serve farmers!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        logger.error("AI agent initialization failed, but API will continue to run")
        krishi_agent = None
        # Don't raise the exception - let the API start without the agent