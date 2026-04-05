from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import get_settings
from app.services.llm import GeminiClientFactory


class ChromaVectorStoreService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        embeddings = GeminiClientFactory().get_embeddings()
        self.vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=embeddings,
            persist_directory=str(settings.chroma_persist_dir),
            client_settings=ChromaSettings(anonymized_telemetry=settings.chroma_anonymized_telemetry),
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        documents = [
            Document(page_content=chunk["chunk_text"], metadata=chunk["metadata"])
            for chunk in chunks
        ]
        ids = [chunk["vector_id"] for chunk in chunks]
        self.vector_store.add_documents(documents=documents, ids=ids)

    def search(self, question: str, top_k: int) -> list[tuple[Document, float]]:
        return self.vector_store.similarity_search_with_score(question, k=top_k)
