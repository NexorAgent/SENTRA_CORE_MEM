from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence
from pathlib import Path
from threading import Lock

import chromadb


@dataclass(slots=True)
class RAGDocument:
    doc_id: str
    text: str
    metadata: Dict[str, Any]


class RAGService:
    def __init__(self, persist_directory: Path) -> None:
        self._persist_directory = persist_directory
        self._persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._persist_directory))
        self._lock = Lock()

    def index(self, collection_name: str, documents: Sequence[RAGDocument]) -> List[str]:
        with self._lock:
            collection = self._client.get_or_create_collection(name=collection_name)
            ids = [doc.doc_id for doc in documents]
            texts = [doc.text for doc in documents]
            metadatas = [self._normalize_metadata(doc.metadata) for doc in documents]
            collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
            return ids

    def query(self, collection_name: str, query_text: str, n_results: int) -> List[Dict[str, Any]]:
        collection = self._client.get_or_create_collection(name=collection_name)
        raw = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        matches: List[Dict[str, Any]] = []
        documents = raw.get("documents") or []
        metadatas = raw.get("metadatas") or []
        distances = raw.get("distances") or []

        for index, document_group in enumerate(documents):
            metadata_group = metadatas[index] if index < len(metadatas) else []
            distance_group = distances[index] if index < len(distances) else []

            for position, excerpt in enumerate(document_group or []):
                metadata = metadata_group[position] if position < len(metadata_group) else {}
                metadata = metadata or {}
                source = metadata.get("source")
                if not source:
                    continue

                score = 0.0
                if position < len(distance_group) and distance_group[position] is not None:
                    raw_score = float(distance_group[position])
                    score = 1.0 - raw_score if 0.0 <= raw_score <= 1.0 else raw_score

                matches.append(
                    {
                        "excerpt": excerpt,
                        "source": str(source),
                        "score": score,
                    }
                )

        return matches

    @staticmethod
    def _normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for key, value in metadata.items():
            normalized[key] = value if isinstance(value, (str, int, float, bool)) else str(value)
        return normalized
