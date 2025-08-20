"""
Knowledge-based tools for Krishi Sahayak AI
Provides access to agricultural research and expertise
Supports both local ChromaDB and remote Pinecone vector stores
"""

import os

# Use langchain_community.embeddings for better compatibility
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langchain_chroma import Chroma
from app.config import Config

# Optional Pinecone imports (only if using remote vector store)
try:
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

def get_vector_store():
    """Get vector store instance based on configuration"""
    if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY and PINECONE_AVAILABLE:
        # Use Pinecone for remote vector store
        try:
            pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Check if index exists
            existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
            if Config.PINECONE_INDEX_NAME not in existing_indexes:
                raise Exception(f"Index {Config.PINECONE_INDEX_NAME} not found")
            
            # Use BAAI/bge-large-en-v1.5 for 1024 dimensions to match Pinecone index
            embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
            index = pc.Index(Config.PINECONE_INDEX_NAME)
            vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
            return vectorstore
            
        except Exception as e:
            print(f"Warning: Pinecone setup failed, falling back to ChromaDB: {e}")
            # Fallback to local ChromaDB
            fallback_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            vectorstore = Chroma(
                persist_directory=Config.VECTOR_STORE_PATH, 
                embedding_function=fallback_embeddings
            )
            return vectorstore
    else:
        # Use local ChromaDB with compatible embedding model  
        local_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vectorstore = Chroma(
            persist_directory=Config.VECTOR_STORE_PATH, 
            embedding_function=local_embeddings
        )
        return vectorstore

@tool
def get_crop_advisory(query: str) -> str:
    """
    Queries the knowledge base for scientific crop advice and agricultural research.
    Contains information from IARI and other agricultural institutions.
    Now supports both local ChromaDB and remote Pinecone vector stores.
    """
    try:
        # Get vector store (Pinecone or ChromaDB based on config)
        vectorstore = get_vector_store()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(query)
        
        if not docs: 
            return "No relevant information found in the knowledge base. Try rephrasing your query or asking about common crops like rice, wheat, or tomato."
        
        # Format the response with source attribution
        response = "Agricultural Research Findings:\n"
        response += "=" * 40 + "\n\n"
        
        for i, doc in enumerate(docs, 1):
            response += f"Research Finding {i}:\n"
            response += f"{doc.page_content}\n"
            if i < len(docs):
                response += "\n" + "-" * 30 + "\n\n"
        
        vector_store_type = "Pinecone" if Config.USE_REMOTE_VECTOR_STORE else "Local ChromaDB"
        response += f"\nSource: Agricultural research database (IARI and associated institutions) via {vector_store_type}"
        return response
        
    except Exception as e:
        return f"An error occurred while fetching crop advisory: {e}"
