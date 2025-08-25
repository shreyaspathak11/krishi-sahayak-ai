import os
import shutil

from typing import List
from langchain_chroma import Chroma
from langchain.schema import Document as LangChainDocument

from ..interface.base_vector_store import BaseVectorStore
from ..interface.base_text_splitter import TextChunk
from ..interface.base_embeddings import BaseEmbeddings


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""

    def __init__(self, persist_directory: str) -> None:
        self.persist_directory = persist_directory
        self.vectorstore = None
        self._load_existing()

    def _load_existing(self) -> bool:
        """Loads existing ChromaDB if it exists."""
        return  os.path.exists(self.persist_directory)
    
    def _ensure_vectorstore_loaded(self, embeddings: BaseEmbeddings)-> None:
        """Ensure vectorstore is loaded with embeddings."""
        if self.vectorstore is None and self._load_existing():
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=embeddings.embeddings
                )
            except Exception as e:
                raise Exception(f"Could not load existing ChromaDB: {str(e)}")

    def add_documents(self, chunks: List[TextChunk], embeddings: BaseEmbeddings) -> None:
        """
            Add documents to the ChromaDB vector store.

            Parameters:
            ----------
            chunks: List[TextChunk]
                The text chunks to add to the vector store.
            embeddings: BaseEmbeddings
                The embeddings to use for the text chunks 
                (embeddings are used to represent the text chunks in the vector store).
        """
        if not chunks:
            raise ValueError("No chunks provided to add to vector store")

        try:
            langchain_docs = []
            for chunk in chunks:
                doc = LangChainDocument(
                    page_content=chunk.content,
                    metadata={
                        "source": chunk.source,
                        **chunk.metadata,
                    }
                )
                langchain_docs.append(doc)

            self.vectorstore = Chroma.from_documents(
                documents=langchain_docs,
                embedding=embeddings.embeddings,
                persist_directory=self.persist_directory
            )

        except Exception as e:
            raise Exception(f"Error adding documents to ChromaDB: {str(e)}")

    def search(self, query: str, embeddings: BaseEmbeddings, top_k: int = 5) -> List[str]:
        """
        Search for similar documents in ChromaDB.

        Parameters:
        ----------
        query: str
            The query string to search for.
        embeddings: BaseEmbeddings
            The embeddings to use for the query.
        top_k: int
            The number of top similar documents to return.

        Returns:
        -------
        List[str]
            A list of the contents of the top similar documents.
        """
        self._ensure_vectorstore_loaded(embeddings)
        
        try:
            results = self.vectorstore.similarity_search(query, k=top_k)
            
            contents = [doc.page_content for doc in results]
            return contents

        except Exception as e:
            return []

    def reset(self) -> None:
        """Reset/clear the ChromaDB vector store."""
        
        try:
            if self._load_existing():
                shutil.rmtree(self.persist_directory)
            self.vectorstore = None
        except Exception as e:
            raise Exception(f"Error resetting ChromaDB: {str(e)}")
