"""
scripts/SQUERY.py
Requêtes sur l’index mémoire comprimée.
Charge la liste brute de blocs depuis `memory/SENTRA_BLOCK_INDEX.json`.
Filtre par intention (⟁INT), agent (⟁ID), date (⟁TS) ou tag (Σ).
Renvoie une réponse formatée et le payload brut.
"""

import json
from pathlib import Path
from datetime import datetime

# Chemin vers l’index mémoire
ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT / "memory" / "SENTRA_BLOCK_INDEX.json"

# Chargement de l’index
def load_index():
    if not INDEX_FILE.exists():
        raise FileNotFoundError(f"Index mémoire introuvable : {INDEX_FILE}")
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))

# Filtrage des blocs
def filter_blocks(index, intent=None, agent=None, date=None, tag=None):
    results = []
    for block in index:
        if intent and intent not in block.get("⟁INT", ""):
            continue
        if agent and agent not in block.get("⟁ID", ""):
            continue
        if date:
            # Compare YYYY-MM-DD
            ts = block.get("⟁TS", "")
            if not ts.startswith(date):
                continue
        if tag and tag not in block.get("Σ", ""):
            continue
        results.append(block)
    return results

# Exécution de la requête extraite du message
def squery_run(message: str) -> dict:
    # Parsing basique des paramètres
    params = { }
    for part in message.split():
        if "=" in part:
            key, val = part.split("=", 1)
            params[key.lower()] = val

    intent = params.get("intent")
    agent  = params.get("agent")
    date   = params.get("date")
    tag    = params.get("tag")

    try:
        index = load_index()
    except FileNotFoundError as e:
        return {"réponse": f"❌ {e}", "glyph": ""}

    filtered = filter_blocks(index, intent=intent, agent=agent, date=date, tag=tag)

    if not filtered:
        return {"réponse": "❌ Aucune donnée mémoire correspondant à la requête.", "glyph": ""}

    # Construction de la réponse humaine
    lines = []
    for blk in filtered:
        lines.append(f"• {blk['⟁ID']} | {blk['⟁TS']} | {blk['⟁INT']} | {blk.get('Σ', '')}")
    response = "\n".join(lines)

    return {"réponse": response, "payload": filtered}

if __name__ == "__main__":
    import sys
    msg = " ".join(sys.argv[1:]) or ""
    print(squery_run(msg))
