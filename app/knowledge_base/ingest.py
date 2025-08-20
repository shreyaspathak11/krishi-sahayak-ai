import os
import sys
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Optional Pinecone imports
try:
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# Import config to check which vector store to use
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.config import Config

# --- CONFIGURATION ---
# Load environment variables from .env file

# Define the paths for source documents and the persistent vector store
SOURCE_DOCUMENTS_DIR = "data/source_documents"
VECTOR_STORE_DIR = "vector_store"

def get_embeddings():
    """Get appropriate embeddings based on vector store configuration"""
    if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
        return HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    else:
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def get_vector_store(embeddings, texts):
    """Create vector store based on configuration"""
    
    if Config.USE_REMOTE_VECTOR_STORE and PINECONE_AVAILABLE and Config.PINECONE_API_KEY:
        
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        
        index = pc.Index(Config.PINECONE_INDEX_NAME)
        
        # Create vector store and add documents in batches
        vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            vectorstore.add_documents(batch)
        
        return vectorstore
    else:
        vectorstore = Chroma.from_documents(
            texts,
            embeddings,
            persist_directory=VECTOR_STORE_DIR
        )
        return vectorstore

def main():
    """
    Enhanced main function to ingest data into either ChromaDB or Pinecone.
    - Loads documents from the source directory.
    - Splits the documents into manageable chunks.
    - Creates appropriate embeddings for the configured vector store.
    - Persists the embeddings in either ChromaDB or Pinecone.
    """
    # Show configuration
    store_type = Config.REMOTE_VECTOR_STORE if Config.USE_REMOTE_VECTOR_STORE else Config.LOCAL_VECTOR_STORE

    # 1. Load documents from the specified directory
    if not os.path.exists(SOURCE_DOCUMENTS_DIR):
        return
    
    loader = DirectoryLoader(
        SOURCE_DOCUMENTS_DIR,
        glob="*.pdf", # Look for all PDF files
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True
    )
    
    try:
        documents = loader.load()
    except Exception as e:
        return
        
    if not documents:
        return

    # 2. Split the loaded documents into smaller text chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # 3. Get appropriate embeddings
    try:
        embeddings = get_embeddings()
    except Exception as e:
        return

    # 4. Create and populate vector store
    try:
        vectorstore = get_vector_store(embeddings, texts)
        print(f"Successfully created {store_type} vector store with {len(texts)} documents")
    except Exception as e:
        return



if __name__ == "__main__":
    # This block ensures the main function runs only when the script is executed directly
    main()