from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class Document(BaseModel):
    """Represents a document with content and metadata."""
    content: str
    source: str
    metadata: dict = {}


class BaseDocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    def load_documents(self, source_dir: str) -> List[Document]:
        """Load documents from a source directory."""
        pass
