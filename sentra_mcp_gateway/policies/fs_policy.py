from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

_DEFAULT_ALLOW = "/projects,/reports,/students,/memory"
_NAME_PATTERN = re.compile(r"^(?P<date>\d{8})_(?P<agent>[a-z0-9\-]+)_(?P<topic>[a-z0-9\-]+)__(?P<slug>[a-z0-9\-]+)\.(?P<ext>[a-z0-9]+)$")


def _allowed_roots() -> list[Path]:
    raw = os.getenv("FS_ROOTS_ALLOW", _DEFAULT_ALLOW)
    roots: list[Path] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        roots.append(Path(chunk))
    return roots or [Path("/projects"), Path("/reports"), Path("/students"), Path("/memory")]


def _is_within(path: Path, roots: Iterable[Path]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\- ]", "", value)
    value = value.replace(" ", "-")
    value = re.sub(r"-+", "-", value)
    return value or "note"


def _build_filename(agent: str, topic: str, slug: str, ext: str = "md") -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"{today}_{slugify(agent)}_{slugify(topic)}__{slugify(slug)}.{ext}"


def ensure_library_path(path_value: str, agent: str | None = None, topic: str | None = None) -> Path:
    if not path_value:
        raise ValueError("Le chemin ne peut pas être vide")
    target = Path(path_value)
    if not target.is_absolute():
        target = Path("/") / target
    target = target.resolve()

    if not _is_within(target, _allowed_roots()):
        allowed = ", ".join(map(str, _allowed_roots()))
        raise ValueError(f"Chemin interdit : {target}. Autorisés : {allowed}")

    if target.is_dir():
        return target

    match = _NAME_PATTERN.match(target.name)
    if match:
        return target

    if agent is None or topic is None:
        raise ValueError(
            "Le nom du fichier doit suivre {YYYY}{MM}{DD}_{agent}_{topic}__{slug}.md ou fournir agent/topic"
        )

    rebuilt = target.with_name(
        _build_filename(agent=agent, topic=topic, slug=target.stem, ext=target.suffix.lstrip("."))
    )
    return rebuilt


def ensure_metadata_source(metadata: dict[str, object], path: Path) -> dict[str, object]:
    metadata = dict(metadata or {})
    source = str(metadata.get("source") or "").strip()
    if not source:
        metadata["source"] = str(path)
        return metadata

    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = Path("/") / source_path
    source_path = source_path.resolve()

    if not _is_within(source_path, _allowed_roots()):
        allowed = ", ".join(map(str, _allowed_roots()))
        raise ValueError(
            f"metadata.source doit pointer vers une ressource autorisée ({allowed})"
        )
    return metadata
