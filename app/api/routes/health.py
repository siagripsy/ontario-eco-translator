from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_engine
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/db/health", response_model=DatabaseHealthResponse)
def db_health_check() -> DatabaseHealthResponse:
    engine = get_engine()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return DatabaseHealthResponse(status="ok")
    except (SQLAlchemyError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"Database health check failed: {exc}") from exc
