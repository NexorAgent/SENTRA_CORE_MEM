from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload


class GoogleCredentialsError(RuntimeError):
    pass


class GoogleAuthManager:
    def __init__(self, credentials_path: Path | None = None) -> None:
        self._credentials_path = self._resolve_credentials_path(credentials_path)

    def _resolve_credentials_path(self, candidate: Path | None) -> Path:
        if candidate and candidate.exists():
            return candidate
        env_path = os.getenv("GOOGLE_CREDENTIALS_FILE")
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path
        default_candidates = [
            Path("/vault/secrets/google_service_account.json"),
            Path("/workspace/secrets/google_service_account.json"),
        ]
        for item in default_candidates:
            if item.exists():
                return item
        raise GoogleCredentialsError("Google service account credentials not found")

    def calendar_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=[
                "https://www.googleapis.com/auth/calendar",
            ],
        )
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)

    def drive_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=[
                "https://www.googleapis.com/auth/drive.file",
            ],
        )
        return build("drive", "v3", credentials=credentials, cache_discovery=False)

    def sheets_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            str(self._credentials_path),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    @staticmethod
    def build_media(body: bytes, mime_type: str):
        return MediaInMemoryUpload(body, mimetype=mime_type, resumable=False)


def serialize_metadata(metadata: Dict[str, Any]) -> str:
    return json.dumps(metadata, sort_keys=True, ensure_ascii=False)
