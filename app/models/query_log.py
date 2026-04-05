from datetime import datetime

from sqlalchemy import Integer, UnicodeText, text
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    answer: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    retrieved_chunks: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2,
        nullable=False,
        server_default=text("SYSUTCDATETIME()"),
    )
