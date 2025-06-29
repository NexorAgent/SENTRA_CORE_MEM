 codex/supprimer-les-marqueurs-de-fusion-et-valider-les-fichiers

 codex/finaliser-scripts-et-tests-de-compression
"""Utility to sanitize the glyph dictionary.

 main
"""scripts/clean_glyph_dict.py
Scinde `memory/glyph_dict.json` en deux :
- Sauvegarde l’ancien dict complet sous `memory/glyph_dict_meta.json`
- Extrait uniquement les paires terme→glyphe (valeur str) vers `memory/glyph_dict.json`
main

- A backup of the existing file is written to ``glyph_dict_meta.json``.
- Only simple ``term -> glyph`` pairs are kept and duplicates are removed.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
MEMORY_DIR = ROOT_DIR / "memory"
GLYPH_PATH = MEMORY_DIR / "glyph_dict.json"
META_PATH = MEMORY_DIR / "glyph_dict_meta.json"

# Load current dictionary
full: dict[str, object] = {}
if GLYPH_PATH.exists():
    full = json.loads(GLYPH_PATH.read_text(encoding="utf-8"))

# Extract only term -> glyph pairs
clean: dict[str, str] = {
    term: glyph for term, glyph in full.items() if isinstance(glyph, str)
}

# Remove duplicate glyphs
reverse: dict[str, str] = {}
duplicates: list[str] = []
for term, glyph in list(clean.items()):
    if glyph in reverse:
        duplicates.append(term)
        del clean[term]
    else:
        reverse[glyph] = term

# Backup and write cleaned dictionary
if GLYPH_PATH.exists():
    GLYPH_PATH.replace(META_PATH)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
GLYPH_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"[clean_glyph_dict] dict épuré écrit dans : {GLYPH_PATH}")
print(f"[clean_glyph_dict] ancien dict sauvegardé dans : {META_PATH}")
codex/supprimer-les-marqueurs-de-fusion-et-valider-les-fichiers

 codex/finaliser-scripts-et-tests-de-compression
if duplicates:
    print("[clean_glyph_dict] doublons supprimés:", duplicates)

from .glyph_generator import _load_dict, _save_dict

if __name__ == "__main__":
    data = _load_dict()
    reverse = {}
    duplicates = []
    for term, glyph in data.items():
        if glyph in reverse:
            duplicates.append(term)
        else:
            reverse[glyph] = term
    for term in duplicates:
        del data[term]
    if duplicates:
        print("Removed duplicates:", duplicates)
        _save_dict(data)
    else:
        print("No duplicates found")
 main
 main
