from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Sequence
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.memory.domain import MemoryNoteDTO
from app.vector.embedding import EmbeddingService, get_embedding_service
from app.db.models.memory import MemoryNote as MemoryNoteModel


class MemoryRepository:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self._embedding_service = embedding_service or get_embedding_service()

    def add_note(
        self,
        session: Session,
        *,
        text: str,
        tags: Sequence[str],
        metadata: dict | None,
        user: str,
        agent: str,
        note_id: str | None = None,
    ) -> tuple[MemoryNoteDTO, bool]:
        normalized_tags = self._normalize_tags(tags)
        payload = json.dumps(
            {"text": text, "tags": normalized_tags, "metadata": metadata or {}},
            sort_keys=True,
            ensure_ascii=False,
        )
        computed_id = note_id or str(uuid5(NAMESPACE_URL, payload))
        existing = session.get(MemoryNoteModel, computed_id)
        if existing:
            return self._to_dto(existing), False

        now = datetime.now(timezone.utc)
        embedding = self._embedding_service.embed([text])[0]
        note = MemoryNoteModel(
            note_id=computed_id,
            user=user,
            agent=agent,
            text=text,
            tags=normalized_tags,
            payload=dict(metadata or {}),
            embedding=embedding,
            created_at=now,
            updated_at=now,
        )
        session.add(note)
        session.flush()
        return self._to_dto(note), True

    def update_timestamp(self, session: Session, note_id: str) -> None:
        note = session.get(MemoryNoteModel, note_id)
        if not note:
            return
        note.updated_at = datetime.now(timezone.utc)
        session.add(note)

    def find_notes(
        self,
        session: Session,
        *,
        query: str,
        tags: Sequence[str] | None,
        limit: int,
    ) -> list[MemoryNoteDTO]:
        normalized_tags = self._normalize_tags(tags or [])
        base_stmt = select(MemoryNoteModel)
        bind = session.get_bind()
        is_postgres = bool(bind and bind.dialect.name == "postgresql")
        if normalized_tags and is_postgres:
            base_stmt = base_stmt.where(MemoryNoteModel.tags.contains(normalized_tags))

        query_text = query.strip()
        if not query_text:
            stmt = base_stmt.order_by(MemoryNoteModel.updated_at.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            if normalized_tags and not is_postgres:
                rows = [row for row in rows if self._tags_match(row.tags, normalized_tags)]
            return [self._to_dto(row) for row in rows]

        return self._vector_search(session, base_stmt, query_text, limit, normalized_tags, is_postgres)

    def _vector_search(
        self,
        session: Session,
        base_stmt: Select[tuple[MemoryNoteModel]],
        query: str,
        limit: int,
        normalized_tags: list[str],
        is_postgres: bool,
    ) -> list[MemoryNoteDTO]:
        embedding = self._embedding_service.embed([query])[0]
        if is_postgres:
            distance = MemoryNoteModel.embedding.cosine_distance(embedding)  # type: ignore[attr-defined]
            stmt = (
                base_stmt.add_columns((1 - distance).label("score"))
                .order_by(distance.asc())
                .limit(limit)
            )
            results = session.execute(stmt).all()
            notes: list[MemoryNoteDTO] = []
            for note, score in results:
                dto = self._to_dto(note)
                dto.score = float(score) if score is not None else None
                notes.append(dto)
            return notes

        rows = session.execute(base_stmt).scalars().all()
        if normalized_tags:
            rows = [row for row in rows if self._tags_match(row.tags, normalized_tags)]
        scored: list[tuple[MemoryNoteModel, float]] = []
        for note in rows:
            if not note.embedding:
                continue
            score = self._cosine_similarity(embedding, note.embedding)
            scored.append((note, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        limited = scored[:limit]
        return [self._to_dto(note, score=score) for note, score in limited]

    def _normalize_tags(self, tags: Sequence[str]) -> list[str]:
        return sorted({tag.strip().lower() for tag in tags if tag and tag.strip()})

    def _tags_match(self, note_tags: Sequence[str], target_tags: Sequence[str]) -> bool:
        note_set = {tag.lower() for tag in note_tags or []}
        return all(tag in note_set for tag in target_tags)

    def _to_dto(self, note: MemoryNoteModel, score: float | None = None) -> MemoryNoteDTO:
        return MemoryNoteDTO(
            note_id=note.note_id,
            user=note.user,
            agent=note.agent,
            text=note.text,
            tags=list(note.tags or []),
            metadata=dict(getattr(note, "payload", {}) or {}),
            created_at=note.created_at,
            updated_at=note.updated_at,
            score=score,
        )

    @staticmethod
    def _cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        if not vector_a or not vector_b:
            return 0.0
        dot = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a * a for a in vector_a) ** 0.5
        norm_b = sum(b * b for b in vector_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
