from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings

from ..interface.base_embeddings import BaseEmbeddings


class HuggingFaceEmbeddingsImpl(BaseEmbeddings):
    """HuggingFace embeddings implementation using LangChain."""

    def __init__(self, model_name: str ):
        self.model_name = model_name
        try:
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        except Exception as e:
            raise Exception(f"Error initializing embeddings: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
            Generate embeddings for a list of texts.

            Parameters:
            ----------
            texts: List[str]
                The list of texts to embed.

            Returns
            -------
            List[List[float]]
                A list of embeddings, one for each input text.
            """
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating document embeddings: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """
            Generate embedding for a single query text.

            Parameters:
            ----------
            text: str
                The query text to embed.

            Returns
            -------
            List[float]
                The embedding for the query text.
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")
