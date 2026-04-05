from sqlalchemy.orm import Session

from app.models.query_log import QueryLog


class QueryLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, question: str, answer: str | None, retrieved_chunks: str | None) -> QueryLog:
        log = QueryLog(question=question, answer=answer, retrieved_chunks=retrieved_chunks)
        self.session.add(log)
        self.session.flush()
        return log
