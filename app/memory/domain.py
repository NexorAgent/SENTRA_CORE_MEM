from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class MemoryNoteDTO:
    note_id: str
    user: str
    agent: str
    text: str
    tags: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    score: float | None = None


@dataclass(slots=True)
class MemoryQueryResult:
    note: MemoryNoteDTO
    score: float
