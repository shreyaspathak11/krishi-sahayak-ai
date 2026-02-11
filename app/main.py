import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import Config
from app.services import create_krishi_agent
from app.tools.knowledge_tools import warm_up_knowledge_base

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- INITIALIZATION ---
app = FastAPI(
    title="Krishi Sahayak API",
    description="AI-powered agricultural assistant for Indian farmers",
    version="2.0.0"
)

# CORS middleware 
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

# Global variable for the AI agent
krishi_agent = None
agent_loading = False  # Track if agent is currently loading


@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent in background so health checks respond immediately."""
    global krishi_agent, agent_loading
    
    logger.info("Starting Krishi Sahayak API...")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    
    # Start agent initialization in background (non-blocking)
    # This allows the server to respond to health checks immediately
    agent_loading = True
    asyncio.create_task(_init_agent_background())


async def _init_agent_background():
    """Background task to initialize the AI agent without blocking the server."""
    global krishi_agent, agent_loading
    
    try:
        # Pre-warm knowledge base if available
        logger.info("Pre-warming components...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, warm_up_knowledge_base)
        
        # Run the CPU-heavy agent creation in a thread pool to not block the event loop
        krishi_agent = await loop.run_in_executor(None, create_krishi_agent)
        
        logger.info("✓ Krishi Sahayak AI agent initialized successfully!")
        logger.info("✓ Ready to serve farmers!")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        logger.error("AI agent initialization failed, but API will continue to run")
        krishi_agent = None
    finally:
        agent_loading = False
