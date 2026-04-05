from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Unicode, UnicodeText, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


class ProcessingRun(Base):
    __tablename__ = "processing_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    run_status: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )
    finished_at: Mapped[datetime | None] = mapped_column(DATETIME2, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="processing_runs")
