from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

from .base_document_loader import Document


class TextChunk(BaseModel):
    """Represents a text chunk with content and metadata."""
    content: str
    source: str
    metadata: dict = {}


class BaseTextSplitter(ABC):
    """Abstract base class for text splitters."""

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[TextChunk]:
        """Split documents into text chunks."""
        pass
