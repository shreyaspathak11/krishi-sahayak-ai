import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from ..interface.base_document_loader import BaseDocumentLoader, Document


class PDFDocumentLoader(BaseDocumentLoader):
    """Document loader for PDF files using LangChain's PyPDFLoader."""

    def load_documents(self, source_dir: str) -> List[Document]:
        """
            Load PDF documents from a source directory.

            Parameter:
            ---------
            source_dir: str
                The path to the directory containing PDF files.

            Returns
            -------
            List[Document]
                A list of loaded Document objects.
        """
        loader = DirectoryLoader(
            source_dir,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )

        try:
            langchain_documents = loader.load()
            documents = []
            
            for doc in langchain_documents:
                document = Document(
                    content=doc.page_content,
                    source=doc.metadata.get("source", ""),
                    metadata=doc.metadata
                )
                documents.append(document)
            return documents
            
        except Exception as e:
            return []
