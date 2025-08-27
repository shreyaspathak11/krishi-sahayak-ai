from typing import List
from langchain.schema import Document as LangChainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.utils.logs import logger

from ..interface.base_text_splitter import BaseTextSplitter, TextChunk
from ..interface.base_document_loader import Document


class RecursiveTextSplitter(BaseTextSplitter):
    """Text splitter using LangChain's RecursiveCharacterTextSplitter."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents: List[Document]) -> List[TextChunk]:
        """Split documents into text chunks."""
        if not documents:
            return []

        try:
            langchain_docs = []
            for doc in documents:
                langchain_doc = LangChainDocument(
                    page_content=doc.content,
                    metadata={"source": doc.source, **doc.metadata}
                )
                langchain_docs.append(langchain_doc)

            # Split using LangChain splitter
            split_docs = self.text_splitter.split_documents(langchain_docs)
            
            # Convert back to our TextChunk format
            chunks = []
            for split_doc in split_docs:
                chunk = TextChunk(
                    content=split_doc.page_content,
                    source=split_doc.metadata.get("source", ""),
                    metadata=split_doc.metadata
                )
                chunks.append(chunk)

            logger.success(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise Exception(f"Error splitting documents: {str(e)}")