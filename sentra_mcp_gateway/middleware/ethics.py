from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_CHARTER_PATH = Path("docs/charte.md")
_AUDIT_PATH = Path("memory/audit.ndjson")


def _charter_version() -> str:
    if not _CHARTER_PATH.exists():
        return "missing"
    digest = hashlib.sha256(_CHARTER_PATH.read_bytes()).hexdigest()
    return digest


def log_charter_read(tool: str, user: str, agent: str | None) -> None:
    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "user": user,
        "agent": agent,
        "charter_version": _charter_version(),
        "event": "charter_read",
    }
    line = json.dumps(record, ensure_ascii=False)
    if _AUDIT_PATH.parent.exists():
        _AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _AUDIT_PATH.open("a", encoding="utf-8") as fp:
            fp.write(line + "\n")
    else:
        print(line)
