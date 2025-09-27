from __future__ import annotations

from pathlib import Path
from typing import Dict


BASE_DIR = Path(__file__).resolve().parents[2]
ALLOWED_ROOTS: Dict[str, Path] = {
    "projects": BASE_DIR / "projects",
    "reports": BASE_DIR / "reports",
    "students": BASE_DIR / "students",
}


def ensure_allowed_root(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_workspace_path(path_value: str) -> Path:
    normalized = path_value.strip()
    if normalized.startswith("/"):
        normalized = normalized[1:]
    parts = normalized.split("/", 1)
    root_key = parts[0]
    if root_key not in ALLOWED_ROOTS:
        raise ValueError("Path must begin with /projects, /reports, or /students")
    base = ALLOWED_ROOTS[root_key]
    ensure_allowed_root(base)
    relative = parts[1] if len(parts) > 1 else ""
    target = (base / relative).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError("Path traversal detected") from exc
    return target
