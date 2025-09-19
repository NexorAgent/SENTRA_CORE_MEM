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

    def query(self, collection_name: str, query_text: str, n_results: int) -> Dict[str, Any]:
        collection = self._client.get_or_create_collection(name=collection_name)
        result = collection.query(query_texts=[query_text], n_results=n_results)
        return result

    @staticmethod
    def _normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}
        for key, value in metadata.items():
            normalized[key] = value if isinstance(value, (str, int, float, bool)) else str(value)
        return normalized
