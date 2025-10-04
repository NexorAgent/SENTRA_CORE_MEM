from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = Field(default="production", description="Current runtime environment label")
    api_title: str = Field(default="SENTRA Core API", description="FastAPI application title")
    api_version: str = Field(default="2.0.0", description="Semantic version of the API")

    base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2])
    memory_library_root: Path = Field(default=Path("memory/library"))
    memory_snapshot_root: Path = Field(default=Path("memory/snapshots"))

    database_url: str = Field(
        default="postgresql+psycopg://sentra:sentra@postgres:5432/sentra_core",
        description="SQLAlchemy database URL (sync engine)",
    )
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=10)

    embedding_backend: str = Field(default="sentence_transformers")
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_device: str | None = Field(default=None)
    embedding_cache_ttl_seconds: int = Field(default=3600)
    embedding_vector_dimension: int = Field(default=384)

    vector_top_k: int = Field(default=8)
    vector_min_score: float = Field(default=0.25)

    allowed_roots: tuple[str, ...] = Field(default=("projects", "reports", "students", "memory"))

    google_credentials_file: str | None = Field(default=None)
    n8n_webhook_url: str | None = Field(default=None)
    sentra_api_base: str = Field(default="http://api:8000")
    mcp_gateway_base_url: str = Field(default="http://mcp:8400/mcp", description="Base URL of the MCP gateway")
    mcp_bridge_timeout_seconds: int = Field(default=30, description="Timeout for MCP bridge requests")

    def resolve_path(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return (self.base_dir / candidate).resolve()

    @property
    def memory_library_path(self) -> Path:
        return self.resolve_path(self.memory_library_root)

    @property
    def memory_snapshot_path(self) -> Path:
        return self.resolve_path(self.memory_snapshot_root)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


