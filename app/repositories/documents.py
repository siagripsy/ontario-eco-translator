from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_document(self, document_name: str, source_type: str, source_path: str, status: str) -> Document:
        document = Document(
            document_name=document_name,
            source_type=source_type,
            source_path=source_path,
            status=status,
        )
        self.session.add(document)
        self.session.flush()
        return document

    def update_status(self, document: Document, status: str) -> Document:
        document.status = status
        self.session.add(document)
        self.session.flush()
        return document

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        self.session.add_all(chunks)
        self.session.flush()

    def list_documents(self) -> list[tuple[Document, int]]:
        chunk_counts = (
            select(
                DocumentChunk.document_id.label("document_id"),
                func.count(DocumentChunk.id).label("chunk_count"),
            )
            .group_by(DocumentChunk.document_id)
            .subquery()
        )

        stmt: Select[tuple[Document, int]] = (
            select(Document, func.coalesce(chunk_counts.c.chunk_count, 0))
            .outerjoin(chunk_counts, chunk_counts.c.document_id == Document.id)
            .order_by(Document.uploaded_at.desc())
        )
        return list(self.session.execute(stmt).all())

    def list_chunks_for_document(self, document_id: int) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc(), DocumentChunk.id.asc())
        )
        return list(self.session.scalars(stmt).all())
