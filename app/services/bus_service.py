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
        payload: Dict[str, Any],
        user: str,
        agent: str,
        idempotency_key: str | None = None,
    ) -> Dict[str, Any]:
        message_id = idempotency_key or str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        row = [
            message_id,
            timestamp,
            user,
            agent,
            serialize_metadata(payload),
            "pending",
            "",
            timestamp,
        ]
        service = self._auth_manager.sheets_service()
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:H",
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error

        dispatch_payload = {
            "workflow": "bus-dispatch",
            "spreadsheet_id": spreadsheet_id,
            "worksheet": worksheet,
            "message_id": message_id,
            "user": user,
            "agent": agent,
            "payload": payload,
            "timestamp": timestamp,
        }
        try:
            self._n8n_client.trigger(dispatch_payload, idempotency_key=message_id)
        except N8NConfigurationError as error:
            raise BusServiceError(str(error)) from error
        except Exception as error:  # pragma: no cover - network errors propagate
            raise BusServiceError(str(error)) from error

        return {
            "message_id": message_id,
            "status": "pending",
            "timestamp": timestamp,
        }

    def poll(self, spreadsheet_id: str, worksheet: str, status: Optional[str], limit: int) -> List[Dict[str, Any]]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:H",
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        values = result.get("values", [])
        records: List[Dict[str, Any]] = []
        for index, row in enumerate(values):
            if index == 0 and row and row[0].lower() == "message_id":
                continue
            record = self._row_to_record(row)
            if not record:
                continue
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
        *,
        agent: str | None = None,
    ) -> Dict[str, Any]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:H",
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        values = result.get("values", [])
        for index, row in enumerate(values, start=1):
            if row and row[0] == message_id:
                padded = list(row) + [""] * max(0, 8 - len(row))
                error_value = error if error is not None else padded[6]
                timestamp = datetime.now(timezone.utc).isoformat()
                update_range = f"{worksheet}!F{index}:H{index}"
                try:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=update_range,
                        valueInputOption="RAW",
                        body={"values": [[status, error_value, timestamp]]},
                    ).execute()
                except HttpError as error:
                    raise BusServiceError(str(error)) from error
                padded[5] = status
                padded[6] = error_value
                padded[7] = timestamp
                record = self._row_to_record(padded)
                if not record:
                    break
                return {
                    "message_id": message_id,
                    "status": status,
                    "timestamp": timestamp,
                }
        raise BusServiceError(f"Message {message_id} not found")

    @staticmethod
    def _row_to_record(row: Sequence[str]) -> Dict[str, Any]:
        if not row:
            return {}
        padded = list(row) + [""] * max(0, 8 - len(row))
        try:
            payload = json.loads(padded[4]) if padded[4] else {}
        except json.JSONDecodeError:
            payload = {}
        status = padded[5] or "pending"
        return {
            "message_id": padded[0],
            "timestamp": padded[1],
            "user": padded[2],
            "agent": padded[3],
            "status": status,
            "payload": payload,
        }
