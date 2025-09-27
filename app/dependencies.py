from __future__ import annotations

from functools import lru_cache

from app.services.audit import AuditLogger
from app.services.git_ops import GitOpsHelper
from app.services.memory_store import MemoryStore
from app.services.n8n_client import N8NClient
from app.services.google_clients import GoogleAuthManager
from app.services.bus_service import BusService
from app.services.rag_service import RAGService
from app.services.paths import BASE_DIR


@lru_cache(maxsize=1)
def get_audit_logger() -> AuditLogger:
    log_path = BASE_DIR / "logs" / "audit.log"
    return AuditLogger(log_path=log_path)


@lru_cache(maxsize=1)
def get_git_helper() -> GitOpsHelper:
    return GitOpsHelper(repo_root=BASE_DIR)


@lru_cache(maxsize=1)
def get_memory_store() -> MemoryStore:
    memory_dir = BASE_DIR / "memory"
    return MemoryStore(memory_dir)


@lru_cache(maxsize=1)
def get_n8n_client() -> N8NClient:
    return N8NClient()


@lru_cache(maxsize=1)
def get_google_auth_manager() -> GoogleAuthManager:
    return GoogleAuthManager()


@lru_cache(maxsize=1)
def get_bus_service() -> BusService:
    return BusService(
        auth_manager=get_google_auth_manager(),
        n8n_client=get_n8n_client(),
    )


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    rag_dir = BASE_DIR / "memory" / "chroma"
    return RAGService(persist_directory=rag_dir)
