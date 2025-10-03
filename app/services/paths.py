from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_base_dir() -> Path:
    settings = get_settings()
    return settings.base_dir


@lru_cache(maxsize=1)
def get_allowed_roots() -> dict[str, Path]:
    settings = get_settings()
    mapping: dict[str, Path] = {}
    for root in settings.allowed_roots:
        root_path = (settings.base_dir / root).resolve()
        root_path.mkdir(parents=True, exist_ok=True)
        mapping[root] = root_path
    return mapping


def resolve_workspace_path(path_value: str) -> Path:
    normalized = path_value.strip()
    if not normalized:
        raise ValueError("Path cannot be empty")
    if normalized.startswith("/"):
        normalized = normalized[1:]
    parts = normalized.split("/", 1)
    root_key = parts[0]
    allowed_roots = get_allowed_roots()
    if root_key not in allowed_roots:
        raise ValueError(
            "Path must begin with one of: " + ", ".join(f"/{name}" for name in allowed_roots)
        )
    base = allowed_roots[root_key]
    relative = parts[1] if len(parts) > 1 else ""
    target = (base / relative).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError("Path traversal detected") from exc
    return target


def ensure_allowed_root(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
