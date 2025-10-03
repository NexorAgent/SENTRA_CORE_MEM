from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, String, Text, types
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base
from app.db.types import VectorType


settings = get_settings()


class MemoryNote(Base):
    __tablename__ = "memory_notes"
    __table_args__ = (
        Index("ix_memory_notes_created_at", "created_at"),
        Index("ix_memory_notes_tags", "tags", postgresql_using="gin"),
    )

    note_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user: Mapped[str] = mapped_column(String(64))
    agent: Mapped[str] = mapped_column(String(64))
    text: Mapped[str] = mapped_column(Text())
    tags: Mapped[list[str]] = mapped_column(types.JSON(), default=list)
    payload: Mapped[dict[str, Any]] = mapped_column(types.JSON(), default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType(settings.embedding_vector_dimension), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


__all__ = ["MemoryNote"]
