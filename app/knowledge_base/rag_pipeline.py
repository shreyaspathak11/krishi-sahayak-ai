from dataclasses import dataclass
from typing import List
import os

from app.knowledge_base.logger_service import error, info, success

from .interface import (
    BaseDocumentLoader,
    BaseTextSplitter,
    BaseEmbeddings,
    BaseVectorStore,
)


@dataclass
class RAGPipeline:
    """Main RAG pipeline that orchestrates document ingestion and vector storage."""

    document_loader: BaseDocumentLoader
    text_splitter: BaseTextSplitter
    embeddings: BaseEmbeddings
    vector_store: BaseVectorStore

    def reset(self) -> None:
        """Reset the vector store."""
        self.vector_store.reset()
        success("Vector store reset complete")

    def ingest_documents(self, source_directory: str) -> bool:
        """
        Complete document ingestion pipeline:
        1. Load documents from source directory
        2. Split documents into chunks
        3. Generate embeddings and store in vector database
        
        Args:
            source_directory: Path to directory containing documents
            
        Returns:
            bool: True if ingestion was successful, False otherwise
        """
        success(f"Starting document ingestion from: {source_directory}")

        # Validate source directory
        if not os.path.exists(source_directory):
            error(f"Source directory does not exist: {source_directory}")
            return False

        try:
            # Step 1: Load documents
            documents = self.document_loader.load_documents(source_directory)
            
            if not documents:
                error("No documents loaded")
                return False

            # Step 2: Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            if not chunks:
                error("No chunks created from documents")
                return False

            # Step 3: Add chunks to vector store
            self.vector_store.add_documents(chunks, self.embeddings)

            success(f"Document ingestion complete! Processed {len(documents)} documents into {len(chunks)} chunks")
            return True

        except Exception as e:
            error(f"Error during document ingestion: {str(e)}")
            return False

    def search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search for relevant documents based on a query.
        
        Args:
            query: The search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant document contents
        """
        try:
            results = self.vector_store.search(query, self.embeddings, top_k)
            
            if results:
                success(f"Found {len(results)} relevant documents")
                for i, result in enumerate(results, 1):
                    info(f"📄 Result {i}: {result[:100]}..." if len(result) > 100 else f"📄 Result {i}: {result}")
            else:
                error("No relevant documents found")

            return results

        except Exception as e:
            error(f"Error during search: {str(e)}")
            return []

    def get_stats(self) -> dict:
        """Get pipeline statistics and configuration."""
        return {
            "document_loader": type(self.document_loader).__name__,
            "text_splitter": type(self.text_splitter).__name__,
            "embeddings": type(self.embeddings).__name__,
            "vector_store": type(self.vector_store).__name__,
        }
