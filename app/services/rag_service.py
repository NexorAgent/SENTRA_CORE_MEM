from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.rag import RAGDocument as RAGDocumentModel
from app.vector.embedding import EmbeddingService, get_embedding_service


@dataclass(slots=True)
class RAGDocument:
    doc_id: str
    text: str
    metadata: Dict[str, Any]


class RAGService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self._embedding_service = embedding_service or get_embedding_service()

    def index(
        self,
        session: Session,
        collection_name: str,
        documents: Sequence[RAGDocument],
    ) -> List[str]:
        if not documents:
            return []
        embeddings = self._embedding_service.embed([doc.text for doc in documents])
        now = datetime.now(timezone.utc)
        indexed_ids: List[str] = []
        for doc, vector in zip(documents, embeddings):
            primary_key = (collection_name, doc.doc_id)
            existing = session.get(RAGDocumentModel, primary_key)
            payload = dict(doc.metadata or {})
            if existing:
                existing.text = doc.text
                existing.payload = payload
                existing.embedding = vector
                existing.updated_at = now
                session.add(existing)
            else:
                record = RAGDocumentModel(
                    collection=collection_name,
                    doc_id=doc.doc_id,
                    text=doc.text,
                    payload=payload,
                    embedding=vector,
                    created_at=now,
                    updated_at=now,
                )
                session.add(record)
            indexed_ids.append(doc.doc_id)
        session.flush()
        return indexed_ids

    def query(
        self,
        session: Session,
        collection_name: str,
        query_text: str,
        n_results: int,
    ) -> List[Dict[str, Any]]:
        embedding = self._embedding_service.embed([query_text])[0]
        base_stmt = select(RAGDocumentModel).where(RAGDocumentModel.collection == collection_name)
        bind = session.get_bind()
        if bind and bind.dialect.name == "postgresql":
            distance = RAGDocumentModel.embedding.cosine_distance(embedding)  # type: ignore[attr-defined]
            stmt = (
                base_stmt.add_columns((1 - distance).label("score"))
                .order_by(distance.asc())
                .limit(n_results)
            )
            rows = session.execute(stmt).all()
            results = []
            for record, score in rows:
                formatted = self._format_result(record, float(score) if score is not None else 0.0)
                if formatted:
                    results.append(formatted)
            return results

        rows = session.execute(base_stmt).scalars().all()
        scored = []
        for record in rows:
            if not record.embedding:
                continue
            score = MemorySearchMixin.cosine_similarity(embedding, record.embedding)
            scored.append((record, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        limited = scored[:n_results]
        results = []
        for record, score in limited:
            formatted = self._format_result(record, score)
            if formatted:
                results.append(formatted)
        return results

    def _format_result(self, record: RAGDocumentModel, score: float) -> Dict[str, Any] | None:
        metadata = dict(getattr(record, "payload", {}) or {})
        source = metadata.get("source")
        if not source:
            return None
        return {
            "excerpt": record.text,
            "source": str(source),
            "score": float(score),
            "metadata": metadata,
        }


class MemorySearchMixin:
    @staticmethod
    def cosine_similarity(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        if not vector_a or not vector_b:
            return 0.0
        dot = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a * a for a in vector_a) ** 0.5
        norm_b = sum(b * b for b in vector_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
