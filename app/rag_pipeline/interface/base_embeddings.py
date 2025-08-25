from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddings(ABC):
    """Abstract base class for embeddings."""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text."""
        pass
