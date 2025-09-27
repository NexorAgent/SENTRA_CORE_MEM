from __future__ import annotations

from datetime import datetime, timezone
import json
import threading
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


class AuditLogger:
    """Write NDJSON audit events with hashed arguments."""

    def __init__(self, log_path: Path) -> None:
        self._log_path = log_path
        self._lock = threading.Lock()

    def log(self, tool_name: str, args: Mapping[str, Any] | None, user: str) -> None:
        payload = json.dumps(args or {}, default=self._default_serializer, sort_keys=True)
        args_hash = sha256(payload.encode("utf-8")).hexdigest()
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "args_hash": args_hash,
            "user": user,
        }
        line = json.dumps(entry, sort_keys=True, ensure_ascii=False)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with self._log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{line}\n")

    @staticmethod
    def _default_serializer(value: Any) -> Any:
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")
