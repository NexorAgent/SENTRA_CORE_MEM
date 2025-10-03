from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from typing import Iterable, List

from app.core.config import get_settings

try:  # pragma: no cover - heavy dependency not exercised in unit tests by default
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None


class EmbeddingService:
    """Provides text embeddings with optional sentence-transformer backend."""

    def __init__(self, model_name: str, device: str | None, dimension: int) -> None:
        self._dimension = dimension
        self._model = None
        if SentenceTransformer is not None:
            try:
                self._model = SentenceTransformer(model_name_or_path=model_name, device=device)
                self._dimension = getattr(self._model, "get_sentence_embedding_dimension", lambda: dimension)()
            except Exception:
                self._model = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        items = list(texts)
        if not items:
            return []
        if self._model is not None:
            vectors = self._model.encode(items, show_progress_bar=False, normalize_embeddings=True)
            return [list(map(float, vec)) for vec in vectors]
        return [self._fallback_embedding(text) for text in items]

    def _fallback_embedding(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        repeated = (digest * math.ceil(self._dimension / len(digest)))[: self._dimension]
        return [b / 255.0 for b in repeated]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(
        model_name=settings.embedding_model_name,
        device=settings.embedding_device,
        dimension=settings.embedding_vector_dimension,
    )
