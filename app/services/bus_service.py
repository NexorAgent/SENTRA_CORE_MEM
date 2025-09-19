from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid4

from googleapiclient.errors import HttpError

from app.services.google_clients import GoogleAuthManager, serialize_metadata


class BusServiceError(RuntimeError):
    pass


class BusService:
    def __init__(self, auth_manager: GoogleAuthManager) -> None:
        self._auth_manager = auth_manager

    def send(self, spreadsheet_id: str, worksheet: str, payload: Dict[str, Any], user: str, agent: str, idempotency_key: str | None = None) -> Dict[str, Any]:
        message_id = idempotency_key or str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        row = [
            message_id,
            timestamp,
            user,
            agent,
            "pending",
            serialize_metadata(payload),
        ]
        service = self._auth_manager.sheets_service()
        try:
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:F",
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        return {"message_id": message_id, "status": "pending", "timestamp": timestamp}

    def poll(self, spreadsheet_id: str, worksheet: str, status: Optional[str], limit: int) -> List[Dict[str, Any]]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:F",
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

    def update_status(self, spreadsheet_id: str, worksheet: str, message_id: str, status: str) -> Dict[str, Any]:
        service = self._auth_manager.sheets_service()
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet}!A:F",
            ).execute()
        except HttpError as error:
            raise BusServiceError(str(error)) from error
        values = result.get("values", [])
        for index, row in enumerate(values, start=1):
            if row and row[0] == message_id:
                update_range = f"{worksheet}!E{index}"
                try:
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=update_range,
                        valueInputOption="RAW",
                        body={"values": [[status]]},
                    ).execute()
                except HttpError as error:
                    raise BusServiceError(str(error)) from error
                return {"message_id": message_id, "status": status}
        raise BusServiceError(f"Message {message_id} not found")

    @staticmethod
    def _row_to_record(row: Sequence[str]) -> Dict[str, Any]:
        padded = list(row) + [""] * max(0, 6 - len(row))
        return {
            "message_id": padded[0],
            "timestamp": padded[1],
            "user": padded[2],
            "agent": padded[3],
            "status": padded[4],
            "payload": json.loads(padded[5]) if padded[5] else {},
        }
