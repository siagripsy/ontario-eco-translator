from types import SimpleNamespace

from langchain_core.documents import Document

from app.schemas.qa import AskRequest
from app.services.qa_service import RAGQAService


class _DummySession:
    def commit(self) -> None:
        return None


class _DummyLogRepository:
    def create(self, question: str, answer: str, retrieved_chunks_json: str) -> None:
        self.last_question = question
        self.last_answer = answer
        self.last_retrieved_chunks_json = retrieved_chunks_json


class _DummyDocumentRepository:
    def list_chunks_for_document(self, document_id: int) -> list[SimpleNamespace]:
        assert document_id == 7
        return [
            SimpleNamespace(chunk_text="Account summary and current charges."),
            SimpleNamespace(chunk_text="Electricity pricing: Time-of-Use. On-peak, Mid-peak, and Off-peak."),
        ]


class _DummyVectorStore:
    def search(self, question: str, top_k: int) -> list[tuple[Document, float]]:
        assert question == "What is my billing plan?"
        assert top_k == 4
        return [
            (
                Document(
                    page_content="Current electricity charges are shown below.",
                    metadata={
                        "document_id": 7,
                        "document_name": "Bill_2.pdf",
                        "chunk_id": 11,
                        "page_number": 2,
                        "section_title": "Electricity charges",
                    },
                ),
                0.12,
            )
        ]


class _UnexpectedChatModel:
    def invoke(self, prompt) -> None:  # pragma: no cover - should never run
        raise AssertionError("LLM should not be called for direct billing-plan questions.")


def test_direct_billing_plan_answer_uses_full_document_detection() -> None:
    service = RAGQAService.__new__(RAGQAService)
    service.session = _DummySession()
    service.settings = SimpleNamespace(retrieval_k=4, max_source_snippet_length=300)
    service.document_repository = _DummyDocumentRepository()
    service.log_repository = _DummyLogRepository()
    service.vector_store = _DummyVectorStore()
    service.chat_model = _UnexpectedChatModel()

    response = service.answer_question(AskRequest(question="What is my billing plan?"))

    assert response.detected_plan == "TOU"
    assert response.answer == "Your billing plan is TOU (Time-of-Use), based on the bill text."
    assert response.detection_confidence >= 0.8
    assert response.sources[0].document_name == "Bill_2.pdf"
