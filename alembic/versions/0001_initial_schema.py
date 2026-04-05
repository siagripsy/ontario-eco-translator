"""Create initial NTPower schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_name", sa.NVARCHAR(length=255), nullable=False),
        sa.Column("source_type", sa.NVARCHAR(length=50), nullable=False),
        sa.Column("source_path", sa.NVARCHAR(length=500), nullable=True),
        sa.Column("uploaded_at", mssql.DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.Column("status", sa.NVARCHAR(length=50), server_default=sa.text("'processed'"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "query_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("question", sa.NVARCHAR(length=None), nullable=False),
        sa.Column("answer", sa.NVARCHAR(length=None), nullable=True),
        sa.Column("retrieved_chunks", sa.NVARCHAR(length=None), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.NVARCHAR(length=None), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_title", sa.NVARCHAR(length=255), nullable=True),
        sa.Column("vector_id", sa.NVARCHAR(length=255), nullable=True),
        sa.Column("created_at", mssql.DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], name="FK_document_chunks_documents"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_chunks_document_id"), "document_chunks", ["document_id"], unique=False)

    op.create_table(
        "processing_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("run_status", sa.NVARCHAR(length=50), nullable=False),
        sa.Column("error_message", sa.NVARCHAR(length=None), nullable=True),
        sa.Column("started_at", mssql.DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.Column("finished_at", mssql.DATETIME2(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], name="FK_processing_runs_documents"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_processing_runs_document_id"), "processing_runs", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_processing_runs_document_id"), table_name="processing_runs")
    op.drop_table("processing_runs")
    op.drop_index(op.f("ix_document_chunks_document_id"), table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("query_logs")
    op.drop_table("documents")
