from collections.abc import Generator

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_connector: Connector | None = None


def _build_local_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.sqlalchemy_local_url,
        pool_pre_ping=True,
        future=True,
    )


def _build_cloud_engine() -> Engine:
    settings = get_settings()
    settings.validate_database_mode()

    ip_type = IPTypes.PRIVATE if settings.cloud_sql_ip_type == "private" else IPTypes.PUBLIC

    global _connector
    _connector = Connector(refresh_strategy="LAZY")

    def get_connection():
        assert _connector is not None
        return _connector.connect(
            settings.cloud_sql_connection_name,
            "pytds",
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            ip_type=ip_type,
        )

    return create_engine(
        "mssql+pytds://",
        creator=get_connection,
        pool_pre_ping=True,
        future=True,
    )


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        settings.validate_database_mode()
        _engine = _build_local_engine() if settings.db_mode == "local" else _build_cloud_engine()
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _session_factory


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
