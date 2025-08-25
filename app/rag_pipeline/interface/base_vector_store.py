from abc import ABC, abstractmethod
from typing import List

from .base_text_splitter import TextChunk
from .base_embeddings import BaseEmbeddings


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(self, chunks: List[TextChunk], embeddings: BaseEmbeddings) -> None:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def search(self, query: str, embeddings: BaseEmbeddings, top_k: int = 5) -> List[str]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset/clear the vector store."""
        pass
