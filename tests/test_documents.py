from fastapi.testclient import TestClient

from app.api.routes import documents
from app.db.session import get_db_session
from app.main import app


class _DummySession:
    def close(self) -> None:
        return None


def test_legacy_document_upload_alias_uses_same_handler(monkeypatch) -> None:
    def fake_ingest_pdf(self, original_filename: str, file_bytes: bytes) -> dict:
        assert original_filename == "sample.pdf"
        assert file_bytes == b"%PDF-1.4 mock pdf bytes"
        return {
            "document_id": 1,
            "document_name": original_filename,
            "status": "processed",
            "chunk_count": 1,
            "processing_run_id": 99,
        }

    app.dependency_overrides[get_db_session] = lambda: _DummySession()
    monkeypatch.setattr(documents.DocumentIngestionService, "ingest_pdf", fake_ingest_pdf)

    client = TestClient(app)
    response = client.post(
        "/document/upload",
        files={"file": ("sample.pdf", b"%PDF-1.4 mock pdf bytes", "application/pdf")},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["document_name"] == "sample.pdf"
