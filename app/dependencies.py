from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.audit import AuditLogger
from app.services.git_ops import GitOpsHelper
from app.memory.service import MemoryService
from app.services.n8n_client import N8NClient
from app.services.google_clients import GoogleAuthManager
from app.services.bus_service import BusService
from app.services.rag_service import RAGService
from app.services.paths import get_base_dir
from app.db.session import get_session


@lru_cache(maxsize=1)
def get_audit_logger() -> AuditLogger:
    settings = get_settings()
    log_path = (settings.base_dir / "logs" / "audit.log").resolve()
    return AuditLogger(log_path=log_path)


@lru_cache(maxsize=1)
def get_git_helper() -> GitOpsHelper:
    base_dir = get_base_dir()
    return GitOpsHelper(repo_root=base_dir)


@lru_cache(maxsize=1)
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache(maxsize=1)
def get_n8n_client() -> N8NClient:
    settings = get_settings()
    return N8NClient(webhook_url=settings.n8n_webhook_url)


@lru_cache(maxsize=1)
def get_google_auth_manager() -> GoogleAuthManager:
    settings = get_settings()
    credentials_path: Path | None = None
    if settings.google_credentials_file:
        credentials_path = settings.resolve_path(Path(settings.google_credentials_file))
    return GoogleAuthManager(credentials_path=credentials_path)


@lru_cache(maxsize=1)
def get_bus_service() -> BusService:
    return BusService(
        auth_manager=get_google_auth_manager(),
        n8n_client=get_n8n_client(),
    )


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService()


def get_db_session() -> Iterator[Session]:
    with get_session() as session:
        yield session
