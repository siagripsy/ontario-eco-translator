from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.processing_run import ProcessingRun


class ProcessingRunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def start(self, document_id: int) -> ProcessingRun:
        run = ProcessingRun(document_id=document_id, run_status="running")
        self.session.add(run)
        self.session.flush()
        return run

    def mark_completed(self, run: ProcessingRun) -> ProcessingRun:
        run.run_status = "completed"
        run.finished_at = datetime.now(timezone.utc)
        self.session.add(run)
        self.session.flush()
        return run

    def mark_failed(self, run: ProcessingRun, error_message: str) -> ProcessingRun:
        run.run_status = "failed"
        run.error_message = error_message
        run.finished_at = datetime.now(timezone.utc)
        self.session.add(run)
        self.session.flush()
        return run
