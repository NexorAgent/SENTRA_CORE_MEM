"""scripts/index_builder.py
Construit /memory/SENTRA_BLOCK_INDEX.json à partir du dernier
fichier *_translated.txt dans logs/.  Appelé automatiquement
par run_auto_translator.

Compatibilité Windows : aucun caractère non‑CP1252 dans les print.
"""

from __future__ import annotations

import base64
import json
import zlib
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent  # …/SENTRA_CORE_MEM_v0.1
LOGS_DIR = ROOT_DIR / "logs"
MEM_DIR = ROOT_DIR / "memory"
MEM_DIR.mkdir(exist_ok=True)
INDEX_FILE = MEM_DIR / "SENTRA_BLOCK_INDEX.json"

# ────────────────────────────
#  Safe print (évite UnicodeEncodeError)
# ────────────────────────────


def safe_print(line: str):
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode())


# ────────────────────────────
#  Helpers
# ────────────────────────────


def _build_block(txt_path: Path) -> dict:
    content = txt_path.read_text(encoding="utf-8", errors="ignore")
    compressed = base64.b85encode(zlib.compress(content.encode())).decode()
    return {
        "⟁ID": "ZFORGE",
        "⟁INT": "FORGE.GEN_AGT",
        "⟁TS": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "Σ": "AUTO_TRANSLATE",
        "⟁CMPZ": compressed,
        "⟁SEAL": "✅SENTRA",
    }


# ────────────────────────────
#  Main
# ────────────────────────────


def main():
    last = max(
        LOGS_DIR.glob("*_translated.txt"), key=lambda p: p.stat().st_mtime, default=None
    )
    if not last:
        safe_print("[index_builder] Aucun fichier traduit trouvé.")
        return

    # Charge l'index existant ou initialise un tableau
    try:
        data = (
            json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            if INDEX_FILE.exists()
            else []
        )
        if isinstance(data, dict):  # index corrompu (compression brute)
            data = []
    except json.JSONDecodeError:
        data = []

    data.append(_build_block(last))
    INDEX_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    safe_print(f"[index_builder] Index mis a jour -> {INDEX_FILE}")


if __name__ == "__main__":
    main()
