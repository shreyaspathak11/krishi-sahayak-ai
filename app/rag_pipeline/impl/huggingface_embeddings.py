from typing import List
import os
from ..interface.base_embeddings import BaseEmbeddings
from app.utils.logs import logger

class HuggingFaceEmbeddingsImpl(BaseEmbeddings):
    """HuggingFace embeddings implementation using LangChain (Remote Inference)."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings = None
        
        # Try to use Remote Inference first (lightweight)
        try:
            from langchain_huggingface import HuggingFaceEndpointEmbeddings
            hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if hf_token:
                logger.info(f"Using remote HuggingFace Inference API for model: {model_name}")
                self.embeddings = HuggingFaceEndpointEmbeddings(
                    model=model_name,
                    task="feature-extraction",
                    huggingfacehub_api_token=hf_token,
                    timeout=60
                )
                return
        except ImportError:
            pass
            
        # Fallback to local (heavy) if remote fails or no token
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            logger.info(f"Using local HuggingFace embeddings for model: {model_name}")
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        except Exception as e:
            # If both fail (e.g. no sentence-transformers installed), raise clear error
            raise Exception(
                f"Could not initialize embeddings. For remote inference, install 'langchain-huggingface' and set HUGGINGFACEHUB_API_TOKEN. "
                f"For local inference, install 'sentence-transformers'. Error: {str(e)}"
            )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating document embeddings: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")
