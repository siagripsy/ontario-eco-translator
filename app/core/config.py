from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import urllib.parse

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Ontario Eco-Translator"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_prefix: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_allow_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]

    db_mode: Literal["local", "cloud"] = "local"
    db_host: str | None = None
    db_port: int = 1433
    db_name: str = "NTPower"
    db_user: str | None = None
    db_password: str | None = None
    db_driver: str = "ODBC Driver 18 for SQL Server"
    cloud_sql_connection_name: str | None = None
    cloud_sql_ip_type: Literal["public", "private"] = "private"
    alembic_database_url: str | None = None

    google_api_key: str | None = None
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"

    chroma_collection_name: str = "ntpower_tariff_chunks"
    chroma_persist_dir: Path = Path("chroma_db")
    chroma_anonymized_telemetry: bool = False
    uploads_dir: Path = Path("data/uploads")

    chunk_size: int = 1200
    chunk_overlap: int = 200
    retrieval_k: int = 4
    max_source_snippet_length: int = 300

    @computed_field
    @property
    def sqlalchemy_local_url(self) -> str:
        self._validate_common_db_settings()
        if not self.db_host:
            raise ValueError("DB_HOST is required when DB_MODE=local.")

       

        odbc_str = (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_host},{self.db_port};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_password};"
            "TrustServerCertificate=yes;"
        )

        params = urllib.parse.quote_plus(odbc_str)

        return f"mssql+pyodbc:///?odbc_connect={params}"

    def _validate_common_db_settings(self) -> None:
        if not self.db_name:
            raise ValueError("DB_NAME is required.")
        if not self.db_user:
            raise ValueError("DB_USER is required.")
        if not self.db_password:
            raise ValueError("DB_PASSWORD is required.")

    def validate_database_mode(self) -> None:
        self._validate_common_db_settings()
        if self.db_mode == "local" and not self.db_host:
            raise ValueError("DB_HOST is required when DB_MODE=local.")
        if self.db_mode == "cloud" and not self.cloud_sql_connection_name:
            raise ValueError("CLOUD_SQL_CONNECTION_NAME is required when DB_MODE=cloud.")

    def validate_gemini_config(self) -> None:
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required for Gemini embeddings and chat.")

    def get_alembic_url(self) -> str:
        if self.alembic_database_url:
            return self.alembic_database_url
        if self.db_mode != "local":
            raise ValueError(
                "Alembic requires ALEMBIC_DATABASE_URL in cloud mode. "
                "Use a direct SQL Server connection string for migrations."
            )
        return self.sqlalchemy_local_url


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
    return settings
