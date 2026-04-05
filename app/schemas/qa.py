from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=10)


class AnswerSource(BaseModel):
    document_id: int | None
    document_name: str | None
    chunk_id: int | None
    page_number: int | None
    section_title: str | None
    snippet: str
    score: float | None = None


class AskResponse(BaseModel):
    answer: str
    detected_plan: str
    detection_confidence: float
    detection_evidence: list[str]
    sources: list[AnswerSource]
