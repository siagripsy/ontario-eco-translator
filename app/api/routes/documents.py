from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.ingestion import DocumentIngestionService

router = APIRouter(prefix="/documents")
legacy_router = APIRouter(prefix="/document")


@router.get("", response_model=list[DocumentListItem])
def list_documents(session: Session = Depends(get_db_session)) -> list[DocumentListItem]:
    ingestion_service = DocumentIngestionService(session)
    return ingestion_service.list_documents()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@legacy_router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
) -> DocumentUploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    ingestion_service = DocumentIngestionService(session)
    return ingestion_service.ingest_pdf(file.filename or "uploaded-document.pdf", contents)
