import json
import os
import pathlib
import random
import re
import string
from typing import Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DICT_PATH = ROOT / "memory" / "glyph_dict.json"
DICT_FILE = pathlib.Path(os.environ.get("GLYPH_DICT_PATH", DEFAULT_DICT_PATH))

GLYPH_POOL = list("↯⊚⟴⚡∑¤†⌇⟁⊕⚙⚖🜁🧩🌀⧉♒︎⩾⊗" + string.punctuation)


def _load_dict() -> Dict[str, str]:
    if DICT_FILE.exists():
        return json.loads(DICT_FILE.read_text(encoding="utf-8"))
    return {}


def _save_dict(d: Dict[str, str]) -> None:
    DICT_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def get_glyph(term: str) -> str:
    """Return glyph for term, generating one if needed."""
    glyphs = _load_dict()
    if term not in glyphs:
        existing = set(glyphs.values())
        glyph = random.choice(GLYPH_POOL) + random.choice("0123456789abcdef")
        while glyph in existing:
            glyph = random.choice(GLYPH_POOL) + random.choice("0123456789abcdef")
        glyphs[term] = glyph
        _save_dict(glyphs)
    return glyphs[term]


def get_term(glyph: str) -> str:
    """Return term associated with glyph, or the glyph itself if unknown."""
    glyphs = _load_dict()
    reverse = {v: k for k, v in glyphs.items()}
    return reverse.get(glyph, glyph)


def compress_text(text: str) -> str:
    """Replace words in text with glyphs."""
    words = re.findall(r"\b\w+\b", text)
    for w in set(words):
        glyph = get_glyph(w)
        pattern = rf"\b{re.escape(w)}\b"
        text = re.sub(pattern, lambda _m, g=glyph: g, text)
    return text


def decompress_text(text: str) -> str:
    """Replace glyphs in text with original terms."""
    glyphs = _load_dict()
    for term, glyph in sorted(glyphs.items(), key=lambda x: len(x[1]), reverse=True):
        text = text.replace(glyph, term)
    return text
