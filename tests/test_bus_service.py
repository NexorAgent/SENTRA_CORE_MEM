from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

import pytest

# Provide a lightweight stub for the Google API client to avoid importing the real package during tests.
import sys
import types

if "googleapiclient" not in sys.modules:
    googleapiclient_module = types.ModuleType("googleapiclient")
    errors_module = types.ModuleType("googleapiclient.errors")
    discovery_module = types.ModuleType("googleapiclient.discovery")
    http_module = types.ModuleType("googleapiclient.http")

    class _HttpError(Exception):
        pass

    def _build(*args: object, **kwargs: object) -> object:
        raise RuntimeError("googleapiclient discovery build should not be called in tests")

    class _MediaInMemoryUpload:  # pragma: no cover - simple stub
        def __init__(self, body: bytes, mimetype: str, resumable: bool = False) -> None:
            self.body = body
            self.mimetype = mimetype
            self.resumable = resumable

    errors_module.HttpError = _HttpError
    discovery_module.build = _build
    http_module.MediaInMemoryUpload = _MediaInMemoryUpload

    googleapiclient_module.errors = errors_module
    discovery_module.build = _build
    http_module.MediaInMemoryUpload = _MediaInMemoryUpload

    sys.modules["googleapiclient"] = googleapiclient_module
    sys.modules["googleapiclient.errors"] = errors_module
    sys.modules["googleapiclient.discovery"] = discovery_module
    sys.modules["googleapiclient.http"] = http_module

if "google" not in sys.modules:
    google_module = types.ModuleType("google")
    sys.modules["google"] = google_module

if "google.oauth2" not in sys.modules:
    oauth2_module = types.ModuleType("google.oauth2")
    sys.modules["google.oauth2"] = oauth2_module
else:
    oauth2_module = sys.modules["google.oauth2"]

service_account_module = types.ModuleType("google.oauth2.service_account")


class _Credentials:  # pragma: no cover - simple stub
    @staticmethod
    def from_service_account_file(*args: object, **kwargs: object) -> object:
        return object()


service_account_module.Credentials = _Credentials
oauth2_module.service_account = service_account_module
sys.modules["google.oauth2.service_account"] = service_account_module
sys.modules["google"].oauth2 = oauth2_module

from app.services import bus_service
from app.services.bus_service import BusService, BusServiceError


class _FakeExecutor:
    def __init__(self, result: Dict[str, Any] | None = None) -> None:
        self._result = result or {}

    def execute(self) -> Dict[str, Any]:
        return self._result


class _FakeValuesResource:
    def __init__(self, values: List[List[str]] | None = None) -> None:
        self.values_data = values or []
        self.append_calls: List[Dict[str, Any]] = []
        self.update_calls: List[Dict[str, Any]] = []

    def append(
        self,
        spreadsheetId: str,
        range: str,
        valueInputOption: str,
        body: Dict[str, Any],
    ) -> _FakeExecutor:
        self.append_calls.append(
            {
                "spreadsheetId": spreadsheetId,
                "range": range,
                "valueInputOption": valueInputOption,
                "body": body,
            }
        )
        return _FakeExecutor()

    def get(self, spreadsheetId: str, range: str) -> _FakeExecutor:  # type: ignore[override]
        return _FakeExecutor({"values": self.values_data})

    def update(
        self,
        spreadsheetId: str,
        range: str,
        valueInputOption: str,
        body: Dict[str, Any],
    ) -> _FakeExecutor:
        self.update_calls.append(
            {
                "spreadsheetId": spreadsheetId,
                "range": range,
                "valueInputOption": valueInputOption,
                "body": body,
            }
        )
        return _FakeExecutor()


class _FakeSpreadsheetsResource:
    def __init__(self, values_resource: _FakeValuesResource) -> None:
        self._values_resource = values_resource

    def values(self) -> _FakeValuesResource:
        return self._values_resource


class _FakeSheetsService:
    def __init__(self, values_resource: _FakeValuesResource) -> None:
        self._spreadsheets = _FakeSpreadsheetsResource(values_resource)

    def spreadsheets(self) -> _FakeSpreadsheetsResource:
        return self._spreadsheets


class _FakeAuthManager:
    def __init__(self, service: _FakeSheetsService) -> None:
        self._service = service

    def sheets_service(self) -> _FakeSheetsService:
        return self._service


class _FakeN8NClient:
    def __init__(self) -> None:
        self.trigger_calls: List[Dict[str, Any]] = []

    def trigger(self, payload: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        self.trigger_calls.append({"payload": payload, "idempotency_key": idempotency_key})
        return {"status": "accepted"}


def _build_service(values: List[List[str]] | None = None) -> tuple[BusService, _FakeValuesResource, _FakeN8NClient]:
    values_resource = _FakeValuesResource(values)
    service = _FakeSheetsService(values_resource)
    auth_manager = _FakeAuthManager(service)
    n8n_client = _FakeN8NClient()
    bus = BusService(auth_manager=auth_manager, n8n_client=n8n_client)
    return bus, values_resource, n8n_client


def test_send_appends_full_row_and_triggers_workflow(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed_timestamp = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    class _FixedDatetime:
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:
            assert tz == timezone.utc
            return fixed_timestamp

    monkeypatch.setattr(bus_service, "datetime", _FixedDatetime)
    monkeypatch.setattr(bus_service, "uuid4", lambda: UUID("12345678-1234-5678-1234-567812345678"))

    bus, values_resource, n8n_client = _build_service()

    payload = {"topic": "Spec review", "goal": "Summarize the draft", "nested": {"x": 1}}

    result = bus.send(
        spreadsheet_id="sheet-123",
        worksheet="Bus",
        payload=payload,
        user="orchestrator",
        agent="codexpert",
    )

    assert len(values_resource.append_calls) == 1
    append_call = values_resource.append_calls[0]
    assert append_call["range"] == "Bus!A:H"
    assert append_call["valueInputOption"] == "RAW"
    appended_row = append_call["body"]["values"][0]
    assert appended_row[0] == "12345678-1234-5678-1234-567812345678"
    assert appended_row[1] == fixed_timestamp.isoformat()
    assert appended_row[2:4] == ["orchestrator", "codexpert"]
    assert appended_row[4] == json.dumps(payload, sort_keys=True, ensure_ascii=False)
    assert appended_row[5:] == ["pending", "", fixed_timestamp.isoformat()]

    assert len(n8n_client.trigger_calls) == 1
    trigger_call = n8n_client.trigger_calls[0]
    assert trigger_call["idempotency_key"] == "12345678-1234-5678-1234-567812345678"
    assert trigger_call["payload"] == {
        "workflow": "bus-dispatch",
        "spreadsheet_id": "sheet-123",
        "worksheet": "Bus",
        "message_id": "12345678-1234-5678-1234-567812345678",
        "user": "orchestrator",
        "agent": "codexpert",
        "payload": payload,
        "timestamp": fixed_timestamp.isoformat(),
    }

    assert result == {
        "message_id": "12345678-1234-5678-1234-567812345678",
        "status": "pending",
        "timestamp": fixed_timestamp.isoformat(),
    }


def test_poll_filters_records_by_status() -> None:
    values = [
        ["message_id", "timestamp", "user", "agent", "payload", "status", "error", "last_update"],
        [
            "msg-1",
            "2024-01-01T00:00:00+00:00",
            "orchestrator",
            "codexpert",
            json.dumps({"alpha": 1}, sort_keys=True, ensure_ascii=False),
            "pending",
            "",
            "2024-01-01T00:00:00+00:00",
        ],
        [
            "msg-2",
            "2024-01-02T00:00:00+00:00",
            "codexpert",
            "orchestrator",
            json.dumps({"beta": 2}, sort_keys=True, ensure_ascii=False),
            "completed",
            "",
            "2024-01-02T00:00:00+00:00",
        ],
    ]

    bus, _, _ = _build_service(values)

    records = bus.poll("sheet-123", "Bus", status="pending", limit=10)
    assert len(records) == 1
    record = records[0]
    assert record["message_id"] == "msg-1"
    assert record["status"] == "pending"
    assert record["payload"] == {"alpha": 1}


def test_update_status_updates_error_and_last_update(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed_timestamp = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)

    class _FixedDatetime:
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:
            assert tz == timezone.utc
            return fixed_timestamp

    monkeypatch.setattr(bus_service, "datetime", _FixedDatetime)

    values = [
        ["message_id", "timestamp", "user", "agent", "payload", "status", "error", "last_update"],
        [
            "msg-1",
            "2024-01-01T00:00:00+00:00",
            "orchestrator",
            "codexpert",
            json.dumps({"alpha": 1}, sort_keys=True, ensure_ascii=False),
            "pending",
            "",
            "2024-01-01T00:00:00+00:00",
        ],
    ]

    bus, values_resource, _ = _build_service(values)

    record = bus.update_status("sheet-123", "Bus", "msg-1", "completed", error="boom")

    assert len(values_resource.update_calls) == 1
    update_call = values_resource.update_calls[0]
    assert update_call["range"] == "Bus!F2:H2"
    assert update_call["body"]["values"][0] == ["completed", "boom", fixed_timestamp.isoformat()]

    assert record == {
        "message_id": "msg-1",
        "status": "completed",
        "timestamp": fixed_timestamp.isoformat(),
    }


def test_update_status_raises_when_message_missing() -> None:
    values = [["message_id", "timestamp", "user", "agent", "payload", "status", "error", "last_update"]]
    bus, _, _ = _build_service(values)

    with pytest.raises(BusServiceError):
        bus.update_status("sheet-123", "Bus", "missing", "done")


def test_update_status_keeps_existing_error_when_not_provided(monkeypatch: pytest.MonkeyPatch) -> None:
    fixed_timestamp = datetime(2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc)

    class _FixedDatetime:
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:
            assert tz == timezone.utc
            return fixed_timestamp

    monkeypatch.setattr(bus_service, "datetime", _FixedDatetime)

    values = [
        ["message_id", "timestamp", "user", "agent", "payload", "status", "error", "last_update"],
        [
            "msg-1",
            "2024-01-01T00:00:00+00:00",
            "orchestrator",
            "codexpert",
            json.dumps({"alpha": 1}, sort_keys=True, ensure_ascii=False),
            "pending",
            "previous-error",
            "2024-01-01T00:00:00+00:00",
        ],
    ]

    bus, values_resource, _ = _build_service(values)

    record = bus.update_status("sheet-123", "Bus", "msg-1", "completed")

    assert values_resource.update_calls[0]["body"]["values"][0] == [
        "completed",
        "previous-error",
        fixed_timestamp.isoformat(),
    ]
    assert record == {
        "message_id": "msg-1",
        "status": "completed",
        "timestamp": fixed_timestamp.isoformat(),
    }
