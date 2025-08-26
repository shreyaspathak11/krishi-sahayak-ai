"""
PDF Document Ingestion Module
Handles loading and processing PDF documents for the vector store.
"""

import os
from typing import List, Optional

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.utils.logs import logger


class PDFDocumentIngester:
    """Handles PDF document loading and processing for vector store ingestion."""
    
    def __init__(self, source_documents_dir: str = "data/source_documents"):
        self.source_documents_dir = source_documents_dir
    
    def load_pdf_documents(self) -> Optional[List[Document]]:
        """Load PDF documents from the source directory."""
        if not os.path.exists(self.source_documents_dir):
            logger.error(f"Source directory not found: {self.source_documents_dir}")
            return None
        
        logger.info(f"Loading documents from: {self.source_documents_dir}")
        
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
                logger.warning("No PDF documents found in source directory")
                return None
            
            logger.success(f"Loaded {len(documents)} PDF documents")
            return documents
        except Exception as e:
            logger.error(f"Failed to load documents: {str(e)}")
            return None
    
    def split_documents(self, documents: List[Document]) -> Optional[List[Document]]:
        """Split documents into chunks."""
        logger.info("Splitting documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        
        try:
            texts = text_splitter.split_documents(documents)
            logger.success(f"Created {len(texts)} text chunks")
            return texts
        except Exception as e:
            logger.error(f"Failed to split documents: {str(e)}")
            return None
    
    def ingest_pdf_documents(self, vectorstore=None) -> bool:
        """Complete PDF document ingestion pipeline."""
        logger.section("PDF Document Ingestion")
        
        documents = self.load_pdf_documents()
        if not documents:
            return False
        
        texts = self.split_documents(documents)
        if not texts:
            return False
        
        if vectorstore:
            try:
                logger.info("Adding documents to vector store")
                vectorstore.add_documents(texts)
                logger.success(f"Successfully added {len(texts)} documents to vector store")
                return True
            except Exception as e:
                logger.error(f"Failed to add documents to vector store: {str(e)}")
                return False
        else:
            logger.success(f"PDF processing completed. {len(texts)} text chunks ready for ingestion")
            return True
    
    def get_pdf_file_count(self) -> int:
        """Get count of PDF files in source directory."""
        if not os.path.exists(self.source_documents_dir):
            return 0
        
        pdf_files = [f for f in os.listdir(self.source_documents_dir) if f.endswith('.pdf')]
        return len(pdf_files)
