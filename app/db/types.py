from __future__ import annotations

import json
from typing import Iterable, Sequence

from sqlalchemy import types
from sqlalchemy.types import TypeDecorator

try:  # pragma: no cover - optional dependency branch
    from pgvector.sqlalchemy import Vector as PgVector
except Exception:  # pragma: no cover - testing without pgvector
    PgVector = None


class VectorType(TypeDecorator):
    """Hybrid vector column supporting pgvector and JSON fallback."""

    cache_ok = True
    impl = types.JSON()

    def __init__(self, dimensions: int, *, as_list: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dimensions = dimensions
        self.as_list = as_list
        self._pg_vector = PgVector(dimensions) if PgVector else None

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if self._pg_vector and dialect.name == "postgresql":
            return dialect.type_descriptor(self._pg_vector)
        return dialect.type_descriptor(types.JSON())

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        as_list = list(value) if not isinstance(value, list) else value
        self._validate_dimensions(as_list)
        if self._pg_vector and dialect.name == "postgresql":
            return as_list
        return as_list

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        if isinstance(value, str):
            as_list = json.loads(value)
        elif isinstance(value, Sequence):
            as_list = list(value)
        else:
            as_list = value
        if len(as_list) != self.dimensions:
            return list(as_list)
        return list(as_list)

    def _validate_dimensions(self, vector: Sequence[float]) -> None:
        if self.dimensions and len(vector) != self.dimensions:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimensions}, got {len(vector)}")

    python_type = list
