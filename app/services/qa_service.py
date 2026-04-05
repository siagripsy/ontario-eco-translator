import json
import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.prompts.rag_prompt import RAG_ANSWER_PROMPT
from app.repositories.query_logs import QueryLogRepository
from app.schemas.qa import AnswerSource, AskRequest, AskResponse
from app.services.knowledge_loader import (
    build_fallback_plan_knowledge,
    load_common_knowledge,
    load_plan_specific_knowledge,
)
from app.services.llm import GeminiClientFactory
from app.services.plan_detection import detect_billing_plan
from app.services.vector_store import ChromaVectorStoreService
from app.utils.text import clip_text

logger = logging.getLogger(__name__)


class RAGQAService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.log_repository = QueryLogRepository(session)
        self.vector_store = ChromaVectorStoreService()
        factory = GeminiClientFactory()
        self.chat_model = factory.get_chat_model()

    def answer_question(self, payload: AskRequest) -> AskResponse:
        top_k = payload.top_k or self.settings.retrieval_k
        retrieved_docs = self.vector_store.search(payload.question, top_k=top_k)

        sources = [
            AnswerSource(
                document_id=document.metadata.get("document_id"),
                document_name=document.metadata.get("document_name"),
                chunk_id=document.metadata.get("chunk_id"),
                page_number=document.metadata.get("page_number"),
                section_title=document.metadata.get("section_title") or None,
                snippet=clip_text(document.page_content, self.settings.max_source_snippet_length),
                score=float(score) if score is not None else None,
            )
            for document, score in retrieved_docs
        ]

        if not sources:
            answer = (
                "I could not find relevant tariff context in the indexed documents, "
                "so I do not have enough information to answer that safely."
            )
            self.log_repository.create(payload.question, answer, "[]")
            self.session.commit()
            return AskResponse(
                answer=answer,
                detected_plan="Unknown",
                detection_confidence=0.0,
                detection_evidence=[],
                sources=[],
            )

        context = "\n\n".join(
            [
                (
                    f"Document: {source.document_name or 'Unknown'}\n"
                    f"Page: {source.page_number or 'Unknown'}\n"
                    f"Section: {source.section_title or 'Unknown'}\n"
                    f"Snippet: {source.snippet}"
                )
                for source in sources
            ]
        )

        detection_text = "\n\n".join(document.page_content for document, _ in retrieved_docs)
        detection = detect_billing_plan(detection_text)
        logger.info(
            "Detected billing plan %s (confidence=%.2f, evidence=%s)",
            detection.detected_plan,
            detection.confidence,
            detection.evidence,
        )

        common_knowledge = load_common_knowledge()
        if detection.detected_plan == "Unknown":
            plan_knowledge = build_fallback_plan_knowledge()
        else:
            plan_knowledge = load_plan_specific_knowledge(detection.detected_plan)

        knowledge_sections = [section for section in (common_knowledge, plan_knowledge) if section]
        knowledge_context = "\n\n".join(knowledge_sections)

        detection_summary = (
            f"Plan: {detection.detected_plan}\n"
            f"Confidence: {detection.confidence:.2f}\n"
            f"Evidence: {', '.join(detection.evidence) if detection.evidence else 'No strong plan clues found.'}"
        )

        prompt = RAG_ANSWER_PROMPT.format_messages(
            question=payload.question,
            context=context,
            detected_plan_summary=detection_summary,
            knowledge_context=knowledge_context,
        )
        answer = self.chat_model.invoke(prompt).content

        retrieved_chunks_json = json.dumps([source.model_dump() for source in sources], ensure_ascii=False)
        self.log_repository.create(payload.question, str(answer), retrieved_chunks_json)
        self.session.commit()

        return AskResponse(
            answer=str(answer),
            detected_plan=detection.detected_plan,
            detection_confidence=detection.confidence,
            detection_evidence=detection.evidence,
            sources=sources,
        )
