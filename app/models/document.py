from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Unicode, UnicodeText, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.processing_run import ProcessingRun


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_name: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    source_type: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    source_path: Mapped[str | None] = mapped_column(Unicode(500), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )
    status: Mapped[str] = mapped_column(
        Unicode(50),
        nullable=False,
        server_default=text("'processed'"),
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    processing_runs: Mapped[list["ProcessingRun"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str | None] = mapped_column(Unicode(255), nullable=True)
    vector_id: Mapped[str | None] = mapped_column(Unicode(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )

    document: Mapped[Document] = relationship(back_populates="chunks")
