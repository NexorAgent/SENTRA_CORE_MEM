from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple
from uuid import uuid5, NAMESPACE_URL
import gzip


@dataclass(slots=True)
class MemoryNote:
    note_id: str
    text: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "MemoryNote":
        return cls(
            note_id=payload["note_id"],
            text=payload["text"],
            tags=list(payload.get("tags", [])),
            metadata=dict(payload.get("metadata", {})),
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
        )


class MemoryStore:
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._json_path = self._base_path / "sentra_memory.json"
        self._archives_dir = self._base_path / "archives"
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._archives_dir.mkdir(parents=True, exist_ok=True)

    def add_note(self, text: str, tags: Sequence[str], metadata: Dict[str, Any], note_id: str | None = None) -> Tuple[MemoryNote, bool]:
        notes = self._load_notes()
        normalized_tags = sorted(set(tags))
        payload = json.dumps({"text": text, "tags": normalized_tags, "metadata": metadata}, sort_keys=True)
        computed_id = note_id or str(uuid5(NAMESPACE_URL, payload))
        now = datetime.now(timezone.utc)
        existing = next((note for note in notes if note.note_id == computed_id), None)
        if existing:
            return existing, False
        new_note = MemoryNote(
            note_id=computed_id,
            text=text,
            tags=list(normalized_tags),
            metadata=dict(metadata),
            created_at=now,
            updated_at=now,
        )
        notes.append(new_note)
        self._write_notes(notes)
        self._write_archive(new_note)
        return new_note, True

    def find_notes(self, query: str, tags: Sequence[str] | None = None, limit: int = 20) -> List[MemoryNote]:
        notes = self._load_notes()
        filtered: Iterable[MemoryNote] = notes
        lowered_query = query.lower()
        if lowered_query:
            filtered = (note for note in filtered if lowered_query in note.text.lower() or lowered_query in json.dumps(note.metadata).lower())
        if tags:
            tags_set = {tag.lower() for tag in tags}
            filtered = (
                note for note in filtered if tags_set.issubset({tag.lower() for tag in note.tags})
            )
        results = []
        for note in filtered:
            results.append(note)
            if len(results) >= limit:
                break
        return results

    def _load_notes(self) -> List[MemoryNote]:
        if not self._json_path.exists():
            return []
        data = json.loads(self._json_path.read_text(encoding="utf-8"))
        return [MemoryNote.from_dict(item) for item in data]

    def _write_notes(self, notes: Sequence[MemoryNote]) -> None:
        serialized = [note.to_dict() for note in notes]
        self._json_path.write_text(json.dumps(serialized, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_archive(self, note: MemoryNote) -> None:
        archive_path = self._archives_dir / f"{note.note_id}.zmem"
        if archive_path.exists():
            return
        payload = json.dumps(note.to_dict(), ensure_ascii=False).encode("utf-8")
        with gzip.open(archive_path, "wb") as handle:
            handle.write(payload)
