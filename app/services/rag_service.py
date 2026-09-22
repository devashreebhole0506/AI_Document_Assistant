from pathlib import Path
from typing import List

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from app.core.config import settings


class RAGService:

    def __init__(self):

        self.persist_directory = (
            "data/chroma"
        )

        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text"
        )

        self.vector_store = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(
        self,
        documents
    ):

        if not documents:
            return 0

        self.vector_store.add_documents(
            documents
        )

        return len(documents)

    def retrieve(
        self,
        query: str,
        k: int = 4
    ):

        return self.vector_store.similarity_search(
            query,
            k=k
        )


rag_service = RAGService()