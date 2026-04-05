import logging
from uuid import uuid4
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document, DocumentChunk
from app.repositories.documents import DocumentRepository
from app.repositories.processing_runs import ProcessingRunRepository
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.pdf_service import PDFTextExtractor
from app.services.text_chunking import TariffChunkingService
from app.services.vector_store import ChromaVectorStoreService
from app.utils.files import build_upload_path, write_bytes_to_file

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.document_repository = DocumentRepository(session)
        self.run_repository = ProcessingRunRepository(session)
        self.pdf_extractor = PDFTextExtractor()
        self.chunking_service = TariffChunkingService()

    def list_documents(self) -> list[DocumentListItem]:
        rows = self.document_repository.list_documents()
        return [
            DocumentListItem(
                id=document.id,
                document_name=document.document_name,
                source_type=document.source_type,
                source_path=document.source_path,
                uploaded_at=document.uploaded_at,
                status=document.status,
                chunk_count=chunk_count,
            )
            for document, chunk_count in rows
        ]

    def ingest_pdf(self, original_filename: str, file_bytes: bytes) -> DocumentUploadResponse:
        upload_path = build_upload_path(self.settings.uploads_dir, original_filename)
        write_bytes_to_file(upload_path, file_bytes)

        document: Document | None = None
        processing_run = None

        try:
            document = self.document_repository.create_document(
                document_name=Path(original_filename).name,
                source_type="pdf_upload",
                source_path=str(upload_path),
                status="processing",
            )
            processing_run = self.run_repository.start(document.id)

            pages = self.pdf_extractor.extract_pages(upload_path)
            if not pages:
                raise ValueError("No extractable text was found in the uploaded PDF.")

            chunk_candidates = self.chunking_service.chunk_pages(pages)
            if not chunk_candidates:
                raise ValueError("No text chunks were generated from the uploaded PDF.")

            chunk_models: list[DocumentChunk] = []
            for chunk in chunk_candidates:
                vector_id = f"doc-{document.id}-chunk-{chunk.chunk_index}-{uuid4().hex[:8]}"
                chunk_models.append(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.chunk_text,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        vector_id=vector_id,
                    )
                )

            self.document_repository.add_chunks(chunk_models)
            self.document_repository.update_status(document, "processed")
            self.run_repository.mark_completed(processing_run)
            self.session.commit()

            vector_payload = [
                {
                    "vector_id": chunk_model.vector_id,
                    "chunk_text": chunk_model.chunk_text,
                    "metadata": {
                        "document_id": chunk_model.document_id,
                        "document_name": document.document_name,
                        "chunk_id": chunk_model.id,
                        "chunk_index": chunk_model.chunk_index,
                        "page_number": chunk_model.page_number,
                        "section_title": chunk_model.section_title or "",
                        "source_path": document.source_path or "",
                    },
                }
                for chunk_model in chunk_models
            ]
            ChromaVectorStoreService().add_chunks(vector_payload)

            self.document_repository.update_status(document, "processed")
            self.run_repository.mark_completed(processing_run)
            self.session.commit()
            logger.info("Processed document %s with %s chunks.", document.id, len(chunk_models))

            return DocumentUploadResponse(
                document_id=document.id,
                document_name=document.document_name,
                status=document.status,
                chunk_count=len(chunk_models),
                processing_run_id=processing_run.id,
            )
        except Exception as exc:
            logger.exception("Document ingestion failed for %s", original_filename)
            self.session.rollback()

            if document is not None and document.id is not None:
                failed_document = self.session.get(Document, document.id)
                failed_run = self.session.get(type(processing_run), processing_run.id) if processing_run else None
                if failed_document is not None:
                    self.document_repository.update_status(failed_document, "failed")
                if failed_run is not None:
                    self.run_repository.mark_failed(failed_run, str(exc))
                self.session.commit()
            else:
                if upload_path.exists():
                    upload_path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=500,
                detail=f"Document upload failed during processing: {exc}",
            ) from exc
