from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, String, Text, types
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.db.base import Base
from app.db.types import VectorType


settings = get_settings()


class RAGDocument(Base):
    __tablename__ = "rag_documents"
    __table_args__ = (
        Index("ix_rag_documents_collection", "collection"),
        Index("ix_rag_documents_created_at", "created_at"),
    )

    collection: Mapped[str] = mapped_column(String(64), primary_key=True)
    doc_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    text: Mapped[str] = mapped_column(Text())
    payload: Mapped[dict[str, Any]] = mapped_column(types.JSON(), default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType(settings.embedding_vector_dimension), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


__all__ = ["RAGDocument"]
