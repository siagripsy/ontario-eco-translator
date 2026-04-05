from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentListItem(BaseModel):
    id: int
    document_name: str
    source_type: str
    source_path: str | None
    uploaded_at: datetime
    status: str
    chunk_count: int

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document_id: int
    document_name: str
    status: str
    chunk_count: int
    processing_run_id: int
