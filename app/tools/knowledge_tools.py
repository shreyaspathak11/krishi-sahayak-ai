"""
Knowledge-based tools for Krishi Sahayak
Agricultural research via Pinecone with lazy-loaded embeddings.
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from langchain_core.tools import tool
from app.config import Config
from app.utils.logs import logger

_vectorstore = None
_initialized = False


def _get_vector_store():
    """Lazily initialize Pinecone vector store on first use."""
    global _vectorstore, _initialized
    
    if _initialized:
        return _vectorstore
    
    _initialized = True
    
    if not Config.PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set")
        return None
    
    try:
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        from langchain_pinecone import PineconeVectorStore
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        
        # Verify index exists
        indexes = [idx["name"] for idx in pc.list_indexes()]
        if Config.PINECONE_INDEX_NAME not in indexes:
            logger.error(f"Index '{Config.PINECONE_INDEX_NAME}' not found")
            return None
        
        # Setup remote embeddings via HuggingFace
        embeddings = HuggingFaceEndpointEmbeddings(
            model=Config.PINECONE_EMBEDDINGS_MODEL,
            task="feature-extraction",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            timeout=60
        )
        
        _vectorstore = PineconeVectorStore(
            index=pc.Index(Config.PINECONE_INDEX_NAME),
            embedding=embeddings
        )
        logger.info("Pinecone initialized")
        return _vectorstore
        
    except Exception as e:
        logger.error(f"Pinecone init failed: {e}")
        return None


@tool
def get_crop_advisory(query: str) -> str:
    """Query knowledge base for agricultural research and crop advice."""
    vectorstore = _get_vector_store()
    
    if not vectorstore:
        return "Knowledge base unavailable. Check Pinecone configuration."
    
    docs = vectorstore.as_retriever(search_kwargs={"k": 3}).invoke(query)
    
    if not docs:
        return "No relevant info found. Try rephrasing or ask about rice, wheat, tomato, etc."
    
    response = "Agricultural Research Findings:\n" + "=" * 40 + "\n\n"
    for i, doc in enumerate(docs, 1):
        response += f"Finding {i}:\n{doc.page_content}\n"
        if i < len(docs):
            response += "\n" + "-" * 30 + "\n\n"
    
    return response + "\nSource: IARI agricultural database via Pinecone"
