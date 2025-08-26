"""
Krishi Sahayak AI - Document Ingestion Pipeline
Handles both PDF documents and KCC (Kisan Call Centre) data ingestion.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Optional

from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Optional Pinecone imports
try:
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from app.config import Config
from app.utils.logs import logger
from .ingest.ingest_kcc import KCCDataIngester
from .ingest.ingest_pdfs import PDFDocumentIngester


class KrishiIngestionPipeline:
    """Document ingestion pipeline for Krishi Sahayak AI."""
    
    def __init__(self):
        self.source_documents_dir = "data/source_documents"
        self.vector_store_dir = "vector_store"
        self.embeddings = None
        self.vectorstore = None
        
        self.pdf_ingester = PDFDocumentIngester(self.source_documents_dir)
        self.kcc_ingester = None
    
    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get embeddings model based on configuration."""
        if self.embeddings is None:
            if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
                model_name = "BAAI/bge-large-en-v1.5"
                logger.info(f"Using optimized embeddings for Pinecone: {model_name}")
            else:
                model_name = "sentence-transformers/all-mpnet-base-v2"
                logger.info(f"Using embeddings for ChromaDB: {model_name}")
            
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
                logger.success("Embeddings model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embeddings model: {str(e)}")
                raise
        
        return self.embeddings
    
    def get_vector_store(self, documents: Optional[List[Document]] = None):
        """Get or create vector store based on configuration."""
        embeddings = self.get_embeddings()
        
        if Config.USE_REMOTE_VECTOR_STORE and PINECONE_AVAILABLE and Config.PINECONE_API_KEY:
            logger.info(f"Using Pinecone vector store: {Config.PINECONE_INDEX_NAME}")
            
            try:
                pc = Pinecone(api_key=Config.PINECONE_API_KEY)
                
                existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
                if Config.PINECONE_INDEX_NAME not in existing_indexes:
                    logger.info(f"Creating new Pinecone index: {Config.PINECONE_INDEX_NAME}")
                    pc.create_index(
                        name=Config.PINECONE_INDEX_NAME,
                        dimension=1024,
                        metric="cosine",
                        spec={
                            "serverless": {
                                "cloud": "aws",
                                "region": "us-east-1"
                            }
                        }
                    )
                    time.sleep(10)
                
                index = pc.Index(Config.PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                if total_vectors > 0:
                    logger.success(f"Connected to existing Pinecone index with {total_vectors:,} vectors")
                
                self.vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
                
                if documents:
                    self._add_documents_to_pinecone(documents)
                
                return self.vectorstore
                
            except Exception as e:
                logger.error(f"Error with Pinecone: {str(e)}")
                raise
        else:
            logger.info(f"Using ChromaDB vector store: {self.vector_store_dir}")
            
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
                logger.error(f"Error with ChromaDB: {str(e)}")
                raise
    
    def _add_documents_to_pinecone(self, documents: List[Document]):
        """Add documents to Pinecone in batches."""
        batch_size = 100
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        logger.info(f"Adding {len(documents)} documents to Pinecone in {total_batches} batches")
        
        for i in range(0, len(documents), batch_size):
            batch_num = i // batch_size + 1
            batch = documents[i:i + batch_size]
            
            logger.progress(batch_num, total_batches, f"Uploading batch {batch_num}/{total_batches}")
            self.vectorstore.add_documents(batch)
        
        logger.success(f"Successfully added {len(documents)} documents to Pinecone")
    
    def ingest_pdf_documents(self) -> bool:
        """Ingest PDF documents using the PDF ingester module."""
        documents = self.pdf_ingester.load_pdf_documents()
        if not documents:
            return False
        
        texts = self.pdf_ingester.split_documents(documents)
        if not texts:
            return False
        
        logger.info("Creating vector store")
        try:
            vectorstore = self.get_vector_store(texts)
            store_type = "Pinecone" if Config.USE_REMOTE_VECTOR_STORE else "ChromaDB"
            logger.success(f"Successfully created {store_type} vector store with {len(texts)} documents")
            return True
        except Exception as e:
            logger.error(f"Failed to create vector store: {str(e)}")
            return False
    
    def ingest_kcc_data(self, max_batches: Optional[int] = None) -> bool:
        """Ingest KCC data using the KCC ingester module."""
        try:
            self.get_vector_store()
        except Exception as e:
            logger.error(f"Failed to initialize vector store for KCC data: {str(e)}")
            return False
        
        self.kcc_ingester = KCCDataIngester(
            vectorstore=self.vectorstore, 
            embeddings=self.embeddings
        )
        
        return self.kcc_ingester.ingest_kcc_data(max_batches)


def main():
    """Main function to execute the document ingestion pipeline."""
    logger.section("Krishi Sahayak AI - Document Ingestion Pipeline")
    logger.info(f"Starting ingestion at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pipeline = KrishiIngestionPipeline()
    
    pdf_success = False
    kcc_success = False
    
    try:
        # 1. Ingest PDF documents
        pdf_count = pipeline.pdf_ingester.get_pdf_file_count()
        if pdf_count > 0:
            logger.info(f"Found {pdf_count} PDF files to process")
            pdf_success = pipeline.ingest_pdf_documents()
        else:
            logger.warning("No PDF files found in source directory")
        
        # 2. Ingest KCC data (if API is configured)
        kcc_configured = (
            hasattr(Config, 'GOV_IN_API_KEY') and 
            hasattr(Config, 'KCC_API_URL') and 
            Config.GOV_IN_API_KEY and 
            Config.KCC_API_URL
        )
        
        if kcc_configured:
            logger.info("KCC API configured, starting KCC data ingestion")
            kcc_success = pipeline.ingest_kcc_data(max_batches=5)
        else:
            logger.warning("KCC API not configured, skipping KCC data ingestion")
        
        # Final status
        logger.section("Ingestion Complete")
        
        if pdf_success and kcc_success:
            logger.success("Both PDF and KCC data ingestion completed successfully")
        elif pdf_success:
            logger.success("PDF document ingestion completed successfully")
            if kcc_configured:
                logger.warning("KCC data ingestion failed")
            else:
                logger.info("KCC data ingestion was skipped (not configured)")
        elif kcc_success:
            logger.success("KCC data ingestion completed successfully")
            logger.warning("PDF document ingestion was skipped or failed")
        else:
            if not pdf_success and not kcc_configured:
                logger.warning("Only basic setup completed - no data sources were configured")
            else:
                logger.error("Ingestion processes failed")
                sys.exit(1)
        
        logger.info(f"Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Unexpected error during pipeline execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()