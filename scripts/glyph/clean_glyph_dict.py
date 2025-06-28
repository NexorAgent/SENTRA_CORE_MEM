"""scripts/clean_glyph_dict.py
Scinde `memory/glyph_dict.json` en deux :
- Sauvegarde l’ancien dict complet sous `memory/glyph_dict_meta.json`
- Extrait uniquement les paires terme→glyphe (valeur str) vers `memory/glyph_dict.json`

Maintient la compatibilité UTF-8 et évite les doublons.
"""
from __future__ import annotations
import json
from pathlib import Path

# Chemins
ROOT_DIR = Path(__file__).resolve().parents[2]
MEMORY_DIR = ROOT_DIR / "memory"
GLYPH_PATH = MEMORY_DIR / "glyph_dict.json"
META_PATH = MEMORY_DIR / "glyph_dict_meta.json"

# 1) Charger l'ancien dict
full = {}
if GLYPH_PATH.exists():
    full = json.loads(GLYPH_PATH.read_text(encoding="utf-8"))

# 2) Extraire paires terme->glyph (valeur str)
clean = {term: glyph for term, glyph in full.items() if isinstance(glyph, str)}

# 3) Sauvegarde de l'ancien
GLYPH_PATH.rename(META_PATH)

# 4) Écriture du nouveau
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
GLYPH_PATH.write_text(
    json.dumps(clean, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"[clean_glyph_dict] dict épuré écrit dans : {GLYPH_PATH}")
print(f"[clean_glyph_dict] ancien dict sauvegardé dans : {META_PATH}")
