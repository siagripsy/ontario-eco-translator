from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.qa import AskRequest, AskResponse
from app.services.qa_service import RAGQAService

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(
    payload: AskRequest,
    session: Session = Depends(get_db_session),
) -> AskResponse:
    service = RAGQAService(session)
    return service.answer_question(payload)
