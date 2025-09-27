from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import sys
import types

if "google" not in sys.modules:
    google_module = types.ModuleType("google")
    sys.modules["google"] = google_module
    oauth2_module = types.ModuleType("google.oauth2")
    sys.modules["google.oauth2"] = oauth2_module
    service_account_module = types.ModuleType("google.oauth2.service_account")

    class _StubCredentials:
        @classmethod
        def from_service_account_file(cls, *args: Any, **kwargs: Any) -> Any:
            return object()

    service_account_module.Credentials = _StubCredentials
    oauth2_module.service_account = service_account_module
    sys.modules["google.oauth2.service_account"] = service_account_module

if "googleapiclient" not in sys.modules:
    googleapiclient_module = types.ModuleType("googleapiclient")
    discovery_module = types.ModuleType("googleapiclient.discovery")
    http_module = types.ModuleType("googleapiclient.http")
    errors_module = types.ModuleType("googleapiclient.errors")

    def _build(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - safety fallback
        raise RuntimeError("googleapiclient.build should not be used in tests")

    class _MediaInMemoryUpload:
        def __init__(self, body: bytes, mimetype: str | None = None, resumable: bool = False) -> None:
            self.body = body
            self.mimetype = mimetype
            self.resumable = resumable

    discovery_module.build = _build
    http_module.MediaInMemoryUpload = _MediaInMemoryUpload
    class _HttpError(Exception):
        pass

    errors_module.HttpError = _HttpError

    googleapiclient_module.discovery = discovery_module
    googleapiclient_module.http = http_module
    googleapiclient_module.errors = errors_module
    sys.modules["googleapiclient"] = googleapiclient_module
    sys.modules["googleapiclient.discovery"] = discovery_module
    sys.modules["googleapiclient.http"] = http_module
    sys.modules["googleapiclient.errors"] = errors_module

if "chromadb" not in sys.modules:
    chromadb_module = types.ModuleType("chromadb")

    class _StubCollection:
        def __init__(self) -> None:
            self.records: Dict[str, Dict[str, Any]] = {}

        def upsert(self, *, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
            for doc_id, doc_text, metadata in zip(ids, documents, metadatas):
                self.records[doc_id] = {"document": doc_text, "metadata": metadata}

        def query(self, *, query_texts: List[str], n_results: int, include: List[str] | None = None) -> Dict[str, Any]:
            query = (query_texts[0] if query_texts else "").lower()
            matches: List[tuple[str, Dict[str, Any]]] = []
            for doc_id, payload in self.records.items():
                document = payload["document"]
                if query and query not in document.lower():
                    continue
                matches.append((doc_id, payload))
                if len(matches) >= n_results:
                    break
            include = include or ["ids", "documents", "metadatas", "distances"]
            result: Dict[str, Any] = {"ids": [[doc_id for doc_id, _ in matches]]}
            if "documents" in include:
                result["documents"] = [[payload["document"] for _, payload in matches]]
            if "metadatas" in include:
                result["metadatas"] = [[payload["metadata"] for _, payload in matches]]
            if "distances" in include:
                result["distances"] = [[0.0 for _ in matches]]
            return result

    class _PersistentClient:
        def __init__(self, path: str) -> None:
            self.path = path
            self._collections: Dict[str, _StubCollection] = {}

        def get_or_create_collection(self, name: str) -> _StubCollection:
            return self._collections.setdefault(name, _StubCollection())

    chromadb_module.PersistentClient = _PersistentClient
    sys.modules["chromadb"] = chromadb_module

import pytest
from fastapi.testclient import TestClient

from app import dependencies as dependencies_module
from app.main import create_app
from app.services import paths as paths_module
from app.services.bus_service import BusServiceError
from app.services.memory_store import MemoryStore


class DummyAuditLogger:
    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def log(self, tool_name: str, args: Dict[str, Any] | None, user: str) -> None:
        self.events.append({"tool": tool_name, "args": args, "user": user})


class DummyGitHelper:
    def __init__(self) -> None:
        self.commits: List[Dict[str, Any]] = []

    def commit_and_push(
        self,
        tool: str,
        file_path: Path,
        agent: str,
        content_hash: str,
        idempotency_key: str | None = None,
    ) -> str:
        path = Path(file_path)
        message = f"[{tool}] {path.name} {content_hash} by {agent}"
        self.commits.append(
            {
                "tool": tool,
                "file": path,
                "agent": agent,
                "hash": content_hash,
                "message": message,
                "idempotency_key": idempotency_key,
            }
        )
        return message


class DummyExecute:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def execute(self) -> Dict[str, Any]:
        return dict(self._payload)


class DummyCalendarService:
    def __init__(self) -> None:
        self.created_events: List[Dict[str, Any]] = []

    class _EventsAPI:
        def __init__(self, service: "DummyCalendarService") -> None:
            self._service = service

        def insert(
            self,
            *,
            calendarId: str,
            body: Dict[str, Any],
            supportsAttachments: bool,
            sendUpdates: str,
        ) -> DummyExecute:
            event_id = body.get("id") or f"event-{len(self._service.created_events) + 1}"
            event = {
                "id": event_id,
                "calendarId": calendarId,
                "body": body,
                "htmlLink": f"https://calendar.google.com/event?eid={event_id}",
                "status": "confirmed",
            }
            self._service.created_events.append(event)
            return DummyExecute({"id": event["id"], "htmlLink": event["htmlLink"], "status": event["status"]})

    def events(self) -> "DummyCalendarService._EventsAPI":
        return DummyCalendarService._EventsAPI(self)


class DummyDriveService:
    def __init__(self) -> None:
        self.uploads: List[Dict[str, Any]] = []

    class _FilesAPI:
        def __init__(self, service: "DummyDriveService") -> None:
            self._service = service

        def create(self, *, body: Dict[str, Any], media_body: Dict[str, Any], fields: str) -> DummyExecute:
            file_id = body.get("id") or f"file-{len(self._service.uploads) + 1}"
            record = {
                "id": file_id,
                "body": dict(body),
                "media": dict(media_body),
                "webViewLink": f"https://drive.google.com/file/d/{file_id}",
            }
            self._service.uploads.append(record)
            return DummyExecute({"id": record["id"], "webViewLink": record["webViewLink"]})

    def files(self) -> "DummyDriveService._FilesAPI":
        return DummyDriveService._FilesAPI(self)


class DummyGoogleAuthManager:
    def __init__(self) -> None:
        self.calendar = DummyCalendarService()
        self.drive = DummyDriveService()

    def calendar_service(self) -> DummyCalendarService:
        return self.calendar

    def drive_service(self) -> DummyDriveService:
        return self.drive

    @staticmethod
    def build_media(body: bytes, mime_type: str) -> Dict[str, Any]:
        return {"body": body, "mime_type": mime_type}


@dataclass
class DummyBusRecord:
    spreadsheet_id: str
    worksheet: str
    message_id: str
    timestamp: str
    user: str
    agent: str
    status: str
    payload: Dict[str, Any]
    error: str
    last_update: str


class DummyBusService:
    def __init__(self) -> None:
        self.records: List[DummyBusRecord] = []

    def send(
        self,
        *,
        spreadsheet_id: str,
        worksheet: str,
        payload: Dict[str, Any],
        user: str,
        agent: str,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        message_id = idempotency_key or f"msg-{len(self.records) + 1}"
        timestamp = f"2024-01-01T00:00:{len(self.records):02d}Z"
        record = DummyBusRecord(
            spreadsheet_id=spreadsheet_id,
            worksheet=worksheet,
            message_id=message_id,
            timestamp=timestamp,
            user=user,
            agent=agent,
            status="pending",
            payload=dict(payload),
            error="",
            last_update=timestamp,
        )
        self.records.append(record)
        return {"message_id": message_id, "status": record.status, "timestamp": timestamp}

    def poll(
        self,
        *,
        spreadsheet_id: str,
        worksheet: str,
        status: str | None,
        limit: int,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for record in self.records:
            if record.spreadsheet_id != spreadsheet_id or record.worksheet != worksheet:
                continue
            if status and record.status.lower() != status.lower():
                continue
            results.append(
                {
                    "message_id": record.message_id,
                    "timestamp": record.timestamp,
                    "user": record.user,
                    "agent": record.agent,
                    "status": record.status,
                    "payload": dict(record.payload),
                }
            )
            if len(results) >= limit:
                break
        return results

    def update_status(
        self,
        *,
        spreadsheet_id: str,
        worksheet: str,
        message_id: str,
        status: str,
        error: str | None = None,
        agent: str | None = None,
    ) -> Dict[str, Any]:
        for record in self.records:
            if (
                record.spreadsheet_id == spreadsheet_id
                and record.worksheet == worksheet
                and record.message_id == message_id
            ):
                record.status = status
                if error is not None:
                    record.error = error
                record.last_update = record.timestamp
                return {
                    "message_id": message_id,
                    "status": status,
                    "timestamp": record.last_update,
                }
        raise BusServiceError(f"Message {message_id} not found")


class DummyRAGService:
    def __init__(self) -> None:
        self.collections: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def index(self, collection_name: str, documents: List[Any]) -> List[str]:
        collection = self.collections.setdefault(collection_name, {})
        ids: List[str] = []
        for document in documents:
            ids.append(document.doc_id)
            collection[document.doc_id] = {"text": document.text, "metadata": dict(document.metadata)}
        return ids

    def query(self, collection_name: str, query_text: str, n_results: int) -> List[Dict[str, Any]]:
        collection = self.collections.get(collection_name, {})
        results: List[Dict[str, Any]] = []
        lowered = query_text.lower()
        for payload in collection.values():
            if lowered not in payload["text"].lower():
                continue
            source = str(payload["metadata"].get("source", ""))
            if not source:
                continue
            results.append(
                {
                    "excerpt": payload["text"],
                    "source": source,
                    "score": 1.0,
                }
            )
            if len(results) >= n_results:
                break
        return results


@pytest.fixture
def api_context(tmp_path, monkeypatch):
    base_dir = tmp_path / "sentra"
    for subdir in ("projects", "reports", "students", "logs", "memory", "archive"):
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(paths_module, "BASE_DIR", base_dir)
    monkeypatch.setattr(
        paths_module,
        "ALLOWED_ROOTS",
        {
            "projects": base_dir / "projects",
            "reports": base_dir / "reports",
            "students": base_dir / "students",
        },
    )

    audit_logger = DummyAuditLogger()
    git_helper = DummyGitHelper()
    memory_store = MemoryStore(base_dir / "memory")
    bus_service = DummyBusService()
    google_manager = DummyGoogleAuthManager()
    rag_service = DummyRAGService()

    return {
        "base_dir": base_dir,
        "audit_logger": audit_logger,
        "audit_events": audit_logger.events,
        "git_helper": git_helper,
        "git_commits": git_helper.commits,
        "memory_store": memory_store,
        "bus_service": bus_service,
        "google_manager": google_manager,
        "rag_service": rag_service,
    }


@pytest.fixture
def client(api_context):
    app = create_app()
    app.dependency_overrides[dependencies_module.get_audit_logger] = lambda: api_context["audit_logger"]
    app.dependency_overrides[dependencies_module.get_git_helper] = lambda: api_context["git_helper"]
    app.dependency_overrides[dependencies_module.get_memory_store] = lambda: api_context["memory_store"]
    app.dependency_overrides[dependencies_module.get_bus_service] = lambda: api_context["bus_service"]
    app.dependency_overrides[dependencies_module.get_google_auth_manager] = lambda: api_context["google_manager"]
    app.dependency_overrides[dependencies_module.get_rag_service] = lambda: api_context["rag_service"]
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
