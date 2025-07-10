# scripts/zblock_generator.py → renommé sentrablock_generator.py

import os
import re
import json
from datetime import datetime
from pathlib import Path

# CONFIGURATION
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "logs"
INDEX_PATH = ROOT_DIR / "memory" / "SENTRA_BLOCK_INDEX.json"

# Initialisation de l'index
if INDEX_PATH.exists():
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
else:
    index_data = {"SENTRA_BLOCKS": []}

# Extraction des blocs glyphiques
for file in LOG_DIR.glob("*_translated.txt"):
    content = file.read_text(encoding="utf-8")
    blocks = re.findall(r"⦿MEM\.BLOCK🧠.*?SEAL⟶.+", content)

    for i, block in enumerate(blocks):
        id_match = re.search(r"⟁ID⟶(\w+)", block)
        ts_match = re.search(r"⟁TS⟶([\d\.T:]+)", block)
        int_match = re.search(r"⟁INT⟶([\w\.\_\+]+)", block)
        glyph_match = re.search(r"⟁Σ⟶(.+?)↯", block)

        if id_match and ts_match and int_match and glyph_match:
            block_entry = {
                "ref": f"⦿MEM.BLOCK🧠::{file.stem}_{i+1:03}",
                "agent": id_match.group(1),
                "date": ts_match.group(1),
                "intent": int_match.group(1),
                "glyph": glyph_match.group(1)
            }
            index_data["SENTRA_BLOCKS"].append(block_entry)

# Sauvegarde de l’index
INDEX_PATH.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"[SENTRA_BLOCK_GENERATOR] Index mis à jour : {INDEX_PATH}")
