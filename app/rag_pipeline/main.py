"""
Krishi Sahayak AI - Comprehensive Document Ingestion Pipeline
Handles both PDF documents and KCC (Kisan Call Centre) data ingestion.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import List, Optional

from langchain.schema import Document
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

# Import configuration and logger
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config import Config

# Simple logger functions (inline to avoid import issues)
import logging

# Setup simple logger
logger = logging.getLogger("KrishiPipeline")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def info(message: str):
    logger.info(f"ℹ️ {message}")

def success(message: str):
    logger.info(f"✅ {message}")

def error(message: str):
    logger.error(f"❌ {message}")

def warning(message: str):
    logger.warning(f"⚠️ {message}")

def status(emoji: str, message: str):
    logger.info(f"{emoji} {message}")

def section(title: str):
    separator = "=" * 60
    logger.info(f"\n{separator}")
    logger.info(f"📝 {title}")
    logger.info(separator)

def progress(current: int, total: int, description: str = ""):
    percentage = (current / total) * 100 if total > 0 else 0
    progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
    message = f"🔄 {description} [{progress_bar}] {current}/{total} ({percentage:.1f}%)"
    print(message, end='\r' if current < total else '\n')


class KrishiIngestionPipeline:
    """Comprehensive ingestion pipeline for Krishi Sahayak AI."""
    
    def __init__(self):
        self.source_documents_dir = "data/source_documents"
        self.vector_store_dir = "vector_store"
        self.cache_dir = "data/kcc_cache"
        self.embeddings = None
        self.vectorstore = None
    
    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get appropriate embeddings based on vector store configuration."""
        if self.embeddings is None:
            if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
                model_name = "BAAI/bge-large-en-v1.5"
                status("🔢", f"Using optimized embeddings for Pinecone: {model_name}")
            else:
                model_name = "sentence-transformers/all-mpnet-base-v2"
                status("🔢", f"Using embeddings for ChromaDB: {model_name}")
            
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
                success("Embeddings model loaded successfully")
            except Exception as e:
                error(f"Failed to load embeddings model: {str(e)}")
                raise
        
        return self.embeddings
    
    def get_vector_store(self, documents: Optional[List[Document]] = None):
        """Get or create vector store based on configuration."""
        embeddings = self.get_embeddings()
        
        if Config.USE_REMOTE_VECTOR_STORE and PINECONE_AVAILABLE and Config.PINECONE_API_KEY:
            status("🌐", f"Using Pinecone vector store: {Config.PINECONE_INDEX_NAME}")
            
            try:
                pc = Pinecone(api_key=Config.PINECONE_API_KEY)
                
                # Check if index exists, create if it doesn't
                existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
                if Config.PINECONE_INDEX_NAME not in existing_indexes:
                    info(f"Creating new Pinecone index: {Config.PINECONE_INDEX_NAME}")
                    pc.create_index(
                        name=Config.PINECONE_INDEX_NAME,
                        dimension=1024,  # BAAI/bge-large-en-v1.5 dimensions
                        metric="cosine",
                        spec={
                            "serverless": {
                                "cloud": "aws",
                                "region": "us-east-1"
                            }
                        }
                    )
                    time.sleep(10)  # Wait for index to be ready
                
                index = pc.Index(Config.PINECONE_INDEX_NAME)
                
                # Check existing data
                stats = index.describe_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                if total_vectors > 0:
                    success(f"Connected to existing Pinecone index with {total_vectors:,} vectors")
                
                self.vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
                
                if documents:
                    self._add_documents_to_pinecone(documents)
                
                return self.vectorstore
                
            except Exception as e:
                error(f"Error with Pinecone: {str(e)}")
                raise
        else:
            status("💾", f"Using ChromaDB vector store: {self.vector_store_dir}")
            
            try:
                if documents:
                    self.vectorstore = Chroma.from_documents(
                        documents,
                        embeddings,
                        persist_directory=self.vector_store_dir
                    )
                else:
                    self.vectorstore = Chroma(
                        persist_directory=self.vector_store_dir,
                        embedding_function=embeddings
                    )
                
                return self.vectorstore
                
            except Exception as e:
                error(f"Error with ChromaDB: {str(e)}")
                raise
    
    def _add_documents_to_pinecone(self, documents: List[Document]):
        """Add documents to Pinecone in batches."""
        batch_size = 100
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        info(f"Adding {len(documents)} documents to Pinecone in {total_batches} batches")
        
        for i in range(0, len(documents), batch_size):
            batch_num = i // batch_size + 1
            batch = documents[i:i + batch_size]
            
            progress(batch_num, total_batches, f"Uploading batch {batch_num}/{total_batches}")
            self.vectorstore.add_documents(batch)
        
        success(f"Successfully added {len(documents)} documents to Pinecone")
    
    def ingest_pdf_documents(self) -> bool:
        """Ingest PDF documents from the source directory."""
        section("PDF Document Ingestion")
        
        # Check if source directory exists
        if not os.path.exists(self.source_documents_dir):
            error(f"Source directory not found: {self.source_documents_dir}")
            return False
        
        status("📂", f"Loading documents from: {self.source_documents_dir}")
        
        # Load documents
        loader = DirectoryLoader(
            self.source_documents_dir,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        
        try:
            documents = loader.load()
            if not documents:
                warning("No PDF documents found in source directory")
                return False
            
            success(f"Loaded {len(documents)} PDF documents")
        except Exception as e:
            error(f"Failed to load documents: {str(e)}")
            return False
        
        # Split documents into chunks
        status("✂️", "Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        
        try:
            texts = text_splitter.split_documents(documents)
            success(f"Created {len(texts)} text chunks")
        except Exception as e:
            error(f"Failed to split documents: {str(e)}")
            return False
        
        # Create/update vector store
        status("💾", "Creating vector store...")
        try:
            vectorstore = self.get_vector_store(texts)
            store_type = "Pinecone" if Config.USE_REMOTE_VECTOR_STORE else "ChromaDB"
            success(f"Successfully created {store_type} vector store with {len(texts)} documents")
            return True
        except Exception as e:
            error(f"Failed to create vector store: {str(e)}")
            return False
    
    def fetch_kcc_data_batch(self, limit: int = 1000, offset: int = 0) -> List[dict]:
        """Fetch KCC data from government API with pagination."""
        if not hasattr(Config, 'GOV_IN_API_KEY') or not hasattr(Config, 'KCC_API_URL'):
            warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return []
        
        if not Config.GOV_IN_API_KEY or not Config.KCC_API_URL:
            warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return []
        
        params = {
            "api-key": Config.GOV_IN_API_KEY,
            "format": "json",
            "limit": limit,
            "offset": offset
        }
        
        try:
            info(f"Fetching KCC records {offset + 1} to {offset + limit}...")
            response = requests.get(Config.KCC_API_URL, params=params, timeout=30)
            response.raise_for_status()
            records = response.json().get("records", [])
            success(f"Successfully fetched {len(records)} KCC records")
            return records
        except Exception as e:
            error(f"Error fetching KCC batch at offset {offset}: {str(e)}")
            return []
    
    def format_kcc_record(self, record: dict) -> Document:
        """Convert KCC record to Document format."""
        state = record.get('StateName', 'Unknown')
        query = record.get('QueryText', 'No query')
        answer = record.get('KccAns', 'No answer')
        crop = record.get('Crop', 'General')
        
        content = f"""
        Farmer Query from {state}:
        {query}

        Expert Answer:
        {answer}

        Crop: {crop}
        Source: Kisan Call Centre
        """
        
        metadata = {
            "source": "KCC",
            "state": state,
            "crop": crop,
            "type": "farmer_query"
        }
        
        return Document(page_content=content, metadata=metadata)
    
    def save_kcc_batch_cache(self, records: List[dict], batch_num: int, timestamp: str) -> Optional[str]:
        """Save KCC batch data to cache file."""
        if not records:
            return None
        
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_filename = f"kcc_batch_{batch_num:03d}_{timestamp}.json"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            info(f"Cached batch {batch_num} to {cache_filename}")
            return cache_path
        except Exception as e:
            error(f"Error caching batch {batch_num}: {str(e)}")
            return None
    
    def ingest_kcc_data(self, max_batches: Optional[int] = None) -> bool:
        """Ingest KCC data from government API."""
        section("KCC Data Ingestion")
        
        if not hasattr(Config, 'GOV_IN_API_KEY') or not hasattr(Config, 'KCC_API_URL'):
            warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return False
        
        if not Config.GOV_IN_API_KEY or not Config.KCC_API_URL:
            warning("KCC API configuration missing. Skipping KCC data ingestion.")
            return False
        
        # Initialize vector store (connect to existing or create new)
        try:
            self.get_vector_store()  # Initialize without documents first
        except Exception as e:
            error(f"Failed to initialize vector store for KCC data: {str(e)}")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_size = 1000
        batch_num = 1
        offset = 0
        total_processed = 0
        failed_batches = []
        
        status("🌐", "Starting KCC data ingestion from government API...")
        
        while True:
            if max_batches and batch_num > max_batches:
                info(f"Reached maximum batch limit: {max_batches}")
                break
            
            info(f"Processing KCC batch {batch_num}...")
            
            # Fetch batch data
            records = self.fetch_kcc_data_batch(limit=batch_size, offset=offset)
            
            if not records:
                info("No more KCC records to fetch. Stopping.")
                break
            
            actual_count = len(records)
            
            # Save batch to cache
            self.save_kcc_batch_cache(records, batch_num, timestamp)
            
            # Convert records to documents
            try:
                documents = [self.format_kcc_record(record) for record in records]
                
                # Add to vector store
                if Config.USE_REMOTE_VECTOR_STORE and self.vectorstore:
                    self.vectorstore.add_documents(documents)
                else:
                    # For ChromaDB, add documents
                    if self.vectorstore:
                        self.vectorstore.add_documents(documents)
                
                total_processed += actual_count
                success(f"Batch {batch_num} processed successfully ({actual_count} records)")
                
            except Exception as e:
                failed_batches.append(batch_num)
                error(f"Batch {batch_num} failed to process: {str(e)}")
            
            info(f"Progress: {total_processed} KCC records processed so far")
            
            # Check if this was the last batch
            if actual_count < batch_size:
                info(f"Last batch detected ({actual_count} < {batch_size})")
                break
            
            # Prepare for next batch
            batch_num += 1
            offset += batch_size
            
            # Add delay to be respectful to the API
            time.sleep(2)
        
        # Final summary
        section("KCC Ingestion Summary")
        success(f"Total KCC records processed: {total_processed}")
        info(f"Total batches processed: {batch_num}")
        
        if failed_batches:
            warning(f"Failed batches: {failed_batches}")
            return False
        else:
            success("All KCC batches processed successfully")
            return True


def main():
    """
    Main function to execute the comprehensive ingestion pipeline.
    """
    section("Krishi Sahayak AI - Document Ingestion Pipeline")
    status("🚀", f"Starting ingestion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pipeline = KrishiIngestionPipeline()
    
    # Determine what to ingest based on available data
    pdf_success = False
    kcc_success = False
    
    try:
        # 1. Ingest PDF documents
        if os.path.exists(pipeline.source_documents_dir):
            pdf_files = [f for f in os.listdir(pipeline.source_documents_dir) if f.endswith('.pdf')]
            if pdf_files:
                status("📄", f"Found {len(pdf_files)} PDF files to process")
                pdf_success = pipeline.ingest_pdf_documents()
            else:
                warning("No PDF files found in source directory")
        else:
            warning(f"Source directory not found: {pipeline.source_documents_dir}")
        
        # 2. Ingest KCC data (if API is configured)
        kcc_configured = (
            hasattr(Config, 'GOV_IN_API_KEY') and 
            hasattr(Config, 'KCC_API_URL') and 
            Config.GOV_IN_API_KEY and 
            Config.KCC_API_URL
        )
        
        if kcc_configured:
            status("📞", "KCC API configured, starting KCC data ingestion")
            kcc_success = pipeline.ingest_kcc_data(max_batches=5)  # Limit for demo
        else:
            warning("KCC API not configured, skipping KCC data ingestion")
        
        # Final status
        section("Ingestion Complete")
        
        if pdf_success and kcc_success:
            success("✅ Both PDF and KCC data ingestion completed successfully!")
        elif pdf_success:
            success("✅ PDF document ingestion completed successfully!")
            if kcc_configured:
                warning("⚠️ KCC data ingestion failed")
            else:
                info("ℹ️ KCC data ingestion was skipped (not configured)")
        elif kcc_success:
            success("✅ KCC data ingestion completed successfully!")
            warning("⚠️ PDF document ingestion was skipped or failed")
        else:
            if not pdf_success and not kcc_configured:
                warning("⚠️ Only basic setup completed - no data sources were configured")
            else:
                error("❌ Ingestion processes failed")
                sys.exit(1)
        
        status("🎉", f"Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        error(f"Unexpected error during pipeline execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()