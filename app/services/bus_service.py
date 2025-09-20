from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4

from googleapiclient.errors import HttpError

from app.services.google_clients import GoogleAuthManager, serialize_metadata
from app.services.n8n_client import N8NClient, N8NConfigurationError


class BusServiceError(RuntimeError):
    pass


class BusService:
    def __init__(self, auth_manager: GoogleAuthManager, n8n_client: N8NClient) -> None:
        self._auth_manager = auth_manager
        self._n8n_client = n8n_client

    def send(
        self,
        spreadsheet_id: str,
        worksheet: str,
        sender: str,
        recipient: str,
        topic: str,
        goal: str,
        context_json: Dict[str, Any],
        user: str,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        message_id = idempotency_key or str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        row = [
            message_id,
            timestamp,
            sender,
            recipient,
            topic,
            goal,
            serialize_metadata(context_json),
            "pending",
            "",
            timestamp,
        ]
        service = self._auth_manager.sheets_service()
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:J",
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error

        dispatch_payload = {
            "workflow": "bus-dispatch",
            "spreadsheet_id": spreadsheet_id,
            "worksheet": worksheet,
            "id": message_id,
            "from": sender,
            "to": recipient,
            "topic": topic,
            "goal": goal,
            "context_json": context_json,
            "ts": timestamp,
        }
        try:
            self._n8n_client.trigger(dispatch_payload, idempotency_key=message_id)
        except N8NConfigurationError as error:
            raise BusServiceError(str(error)) from error
        except Exception as error:  # pragma: no cover - network errors propagate
            raise BusServiceError(str(error)) from error

        return {
            "id": message_id,
            "ts": timestamp,
            "from": sender,
            "to": recipient,
            "topic": topic,
            "goal": goal,
            "context_json": context_json,
            "status": "pending",
            "error": "",
            "last_update": timestamp,
        }

    def poll(self, spreadsheet_id: str, worksheet: str, status: Optional[str], limit: int) -> List[Dict[str, Any]]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:J",
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        values = result.get("values", [])
        records: List[Dict[str, Any]] = []
        for row in values[1:]:
            record = self._row_to_record(row)
            if status and record["status"].lower() != status.lower():
                continue
            records.append(record)
            if len(records) >= limit:
                break
        return records

    def update_status(
        self,
        spreadsheet_id: str,
        worksheet: str,
        message_id: str,
        status: str,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:J",
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        values = result.get("values", [])
        for index, row in enumerate(values, start=1):
            if row and row[0] == message_id:
                padded = list(row) + [""] * max(0, 10 - len(row))
                error_value = error if error is not None else padded[8]
                timestamp = datetime.now(timezone.utc).isoformat()
                update_range = f"{worksheet}!H{index}:J{index}"
                try:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=update_range,
                        valueInputOption="RAW",
                        body={"values": [[status, error_value, timestamp]]},
                    ).execute()
                except HttpError as error:
                    raise BusServiceError(str(error)) from error
                padded[7] = status
                padded[8] = error_value
                padded[9] = timestamp
                return self._row_to_record(padded)
        raise BusServiceError(f"Message {message_id} not found")

    @staticmethod
    def _row_to_record(row: Sequence[str]) -> Dict[str, Any]:
        padded = list(row) + [""] * max(0, 10 - len(row))
        try:
            context = json.loads(padded[6]) if padded[6] else {}
        except json.JSONDecodeError:
            context = {}
        return {
            "id": padded[0],
            "ts": padded[1],
            "from": padded[2],
            "to": padded[3],
            "topic": padded[4],
            "goal": padded[5],
            "context_json": context,
            "status": padded[7],
            "error": padded[8],
            "last_update": padded[9],
        }
