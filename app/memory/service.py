from __future__ import annotations

import json
import gzip
from pathlib import Path
from typing import Sequence

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.memory.domain import MemoryNoteDTO
from app.memory.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository | None = None) -> None:
        self._repository = repository or MemoryRepository()
        settings = get_settings()
        self._archive_dir = settings.memory_library_path / "archives"
        self._archive_dir.mkdir(parents=True, exist_ok=True)

    def add_note(
        self,
        session: Session,
        *,
        user: str,
        agent: str,
        text: str,
        tags: Sequence[str],
        metadata: dict | None,
        note_id: str | None = None,
    ) -> tuple[MemoryNoteDTO, bool]:
        note, created = self._repository.add_note(
            session,
            text=text,
            tags=tags,
            metadata=metadata or {},
            user=user,
            agent=agent,
            note_id=note_id,
        )
        if created:
            self._write_archive(note)
        return note, created

    def find_notes(
        self,
        session: Session,
        *,
        query: str,
        tags: Sequence[str] | None,
        limit: int,
    ) -> list[MemoryNoteDTO]:
        return self._repository.find_notes(session, query=query, tags=tags, limit=limit)

    def _write_archive(self, note: MemoryNoteDTO) -> None:
        payload = {
            "note_id": note.note_id,
            "user": note.user,
            "agent": note.agent,
            "text": note.text,
            "tags": note.tags,
            "metadata": note.metadata,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
        archive_path = self._archive_dir / f"{note.note_id}.zmem"
        if archive_path.exists():
            return
        with gzip.open(archive_path, "wt", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
