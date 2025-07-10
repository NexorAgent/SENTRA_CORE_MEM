import pathlib
import re
from typing import Set

from .glyph_generator import get_glyph


def _extract_terms(text: str) -> Set[str]:
    return set(re.findall(r"\b\w+\b", text))


def scan_directory(log_dir: str | pathlib.Path) -> Set[str]:
    """Scan directory for text files and register new glyphs."""
    log_dir = pathlib.Path(log_dir)
    terms: Set[str] = set()
    for path in log_dir.glob("*.txt"):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        terms.update(_extract_terms(content))
    for term in terms:
        get_glyph(term)
    return terms
