from app.utils.logs import logger
from ..config import Config
from .interface import BaseDocumentLoader, BaseTextSplitter, BaseEmbeddings, BaseVectorStore
from .impl import (
    PDFDocumentLoader,
    RecursiveTextSplitter,
    HuggingFaceEmbeddingsImpl,
    ChromaVectorStore,
    PineconeVectorStore
)
from .rag_pipeline import RAGPipeline


class RAGPipelineFactory:
    """Factory class for creating RAG pipeline components based on configuration."""

    @staticmethod
    def create_document_loader() -> BaseDocumentLoader:
        """Create document loader based on configuration."""
        return PDFDocumentLoader()

    @staticmethod
    def create_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 200) -> BaseTextSplitter:
        """Create text splitter based on configuration."""
        return RecursiveTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    @staticmethod
    def create_embeddings() -> BaseEmbeddings:
        """Create embeddings based on configuration."""
        if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
            model_name = Config.PINECONE_EMBEDDINGS_MODEL
        else:
            model_name = Config.CHROMA_EMBEDDINGS_MODEL
        
        return HuggingFaceEmbeddingsImpl(model_name=model_name)

    @staticmethod
    def create_vector_store() -> BaseVectorStore:
        """Create vector store based on configuration."""
        if Config.USE_REMOTE_VECTOR_STORE and Config.PINECONE_API_KEY:
            return PineconeVectorStore(
                api_key=Config.PINECONE_API_KEY,
                index_name=Config.PINECONE_INDEX_NAME
            )
        else:
            return ChromaVectorStore(persist_directory=Config.LOCAL_VECTOR_STORE)

    @classmethod
    def create_pipeline(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> RAGPipeline:
        """
        Create a complete RAG pipeline with all components.
        
        Args:
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between consecutive chunks
            
        Returns:
            Configured RAGPipeline instance
        """
        document_loader = self.create_document_loader()
        text_splitter = self.create_text_splitter(chunk_size, chunk_overlap)
        embeddings = self.create_embeddings()
        vector_store = self.create_vector_store()

        pipeline = RAGPipeline(
            document_loader=document_loader,
            text_splitter=text_splitter,
            embeddings=embeddings,
            vector_store=vector_store
        )

        logger.success("RAG pipeline created successfully!")
        return pipeline
