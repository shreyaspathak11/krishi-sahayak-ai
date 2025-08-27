from typing import List, Optional
from langchain_pinecone import PineconeVectorStore as LangChainPineconeVectorStore
from langchain.schema import Document as LangChainDocument
from pinecone import Pinecone

from ..interface.base_vector_store import BaseVectorStore
from ..interface.base_text_splitter import TextChunk
from ..interface.base_embeddings import BaseEmbeddings
from ...utils.logs import logger


class PineconeVectorStore(BaseVectorStore):
    """Pinecone vector store implementation."""

    def __init__(self, api_key: str, index_name: str) -> None:
        self.api_key = api_key
        self.index_name = index_name
        self.vectorstore: Optional[LangChainPineconeVectorStore] = None
        
        try:
            self.pinecone = Pinecone(api_key=api_key)
            self.index = self.pinecone.Index(index_name)
            self._check_existing_data()
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            raise Exception(f"Error initializing Pinecone: {str(e)}")

    def _check_existing_data(self):
        """Check if the index already has data."""
        try:
            stats = self.index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            if total_vectors > 0:
                logger.success(f"Connected to existing Pinecone index with {total_vectors:,} vectors")
            else:
                logger.warning("Pinecone index is empty")       
        except Exception as e:
            logger.error(f"Error checking Pinecone index stats: {str(e)}")
            raise Exception(f"Error checking Pinecone index stats: {str(e)}")

    def _ensure_vectorstore_loaded(self, embeddings: BaseEmbeddings):
        """Ensure vectorstore is loaded with embeddings."""
        if self.vectorstore is None:
            try:
                logger.info("Loading Pinecone vectorstore with embeddings...")
                self.vectorstore = LangChainPineconeVectorStore(
                    index=self.index,
                    embedding=embeddings.embeddings
                )
                logger.success("Pinecone vectorstore loaded successfully")
            except Exception as e:
                logger.error(f"Error ensuring vectorstore is loaded: {str(e)}")
                raise Exception(f"Error ensuring vectorstore is loaded: {str(e)}")

    def add_documents(self, chunks: List[TextChunk], embeddings: BaseEmbeddings) -> None:
        """Add documents to the Pinecone vector store."""
        if not chunks:
            logger.warning("No chunks provided to add to vector store")
            raise ValueError("No chunks provided to add to vector store")

        logger.info(f"Adding {len(chunks)} documents to Pinecone...")

        try:            
            langchain_docs = []
            for chunk in chunks:
                doc = LangChainDocument(
                    page_content=chunk.content,
                    metadata={"source": chunk.source, **chunk.metadata,}
                )
                langchain_docs.append(doc)

            # Ensure vectorstore is connected
            self._ensure_vectorstore_loaded(embeddings)
            
            if not self.vectorstore:
                # Create new Pinecone vector store
                logger.info("Creating new Pinecone vector store...")
                self.vectorstore = LangChainPineconeVectorStore(
                    index=self.index,
                    embedding=embeddings.embeddings 
                )

            # Add documents in batches
            batch_size = 100
            total_batches = (len(langchain_docs) + batch_size - 1) // batch_size
            
            for i in range(0, len(langchain_docs), batch_size):
                batch_num = i // batch_size + 1
                batch = langchain_docs[i:i + batch_size]
                
                logger.progress(batch_num, total_batches, f"Uploading batch {batch_num}/{total_batches}")
                self.vectorstore.add_documents(batch)

            logger.success(f"Successfully added {len(chunks)} documents to Pinecone")

        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {str(e)}")
            raise Exception(f"Error adding documents to Pinecone: {str(e)}")

    def search(self, query: str, embeddings: BaseEmbeddings, top_k: int = 5) -> List[str]:
        """Search for similar documents in Pinecone."""
        logger.info(f"Searching for: '{query}' (top {top_k} results)")
        
        # Ensure vectorstore is loaded
        self._ensure_vectorstore_loaded(embeddings)
        
        if not self.vectorstore:
            logger.error("Vector store not initialized and could not connect to existing data")
            return []

        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=top_k)
            
            # Extract content from results
            contents = [doc.page_content for doc in results]
            logger.success(f"Found {len(contents)} similar documents")
            return contents

        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}")
            return []

    def reset(self) -> None:
        """Reset/clear the Pinecone vector store."""
        try:
            logger.warning("Resetting Pinecone index...")
            # Delete all vectors from the index
            self.index.delete(delete_all=True)
            logger.success(f"Reset Pinecone index: {self.index_name}")
            self.vectorstore = None
        except Exception as e:
            logger.error(f"Error resetting Pinecone index: {str(e)}")
            raise
