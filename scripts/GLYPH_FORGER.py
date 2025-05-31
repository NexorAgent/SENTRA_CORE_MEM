import json
import pathlib
import random
import string

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLYPH_DICT = ROOT / "memory" / "glyph_dict.json"

# Exemple de stock de symboles libres / à étendre
GLYPH_POOL = list("↯⊚⟴⚡∑¤†⌇⟁⊕⚙⚖🜁🧩🌀⧉♒︎⩾⊗" + string.punctuation)

def _load_dict():
    if GLYPH_DICT.exists():
        return json.loads(GLYPH_DICT.read_text(encoding="utf-8"))
    return {}

def _save_dict(d):
    GLYPH_DICT.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

def forge_glyph(term: str) -> str:
    glyphs = _load_dict()
    if term in glyphs:
        return glyphs[term]
    # génération locale naïve (améliorable)
    new = random.choice(GLYPH_POOL) + random.choice("*~^@")
    glyphs[term] = new
    _save_dict(glyphs)
    return new