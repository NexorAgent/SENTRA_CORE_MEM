# ───────────────────────────────────────────────────────────
# scripts/memory_lookup.py
# Module pour rechercher du contenu dans memory/sentra_memory.json
# ───────────────────────────────────────────────────────────

import json
from pathlib import Path
from typing import List, Dict

def load_memory_entries() -> List[Dict]:
    """
    Charge toutes les entrées JSON (une par ligne) dans memory/sentra_memory.json.
    """
    project_root = Path(__file__).resolve().parent.parent
    memory_file = project_root / "memory" / "sentra_memory.json"
    if not memory_file.exists():
        return []

    entries = []
    with memory_file.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def search_memory(query: str, max_results: int = 5) -> List[str]:
    """
    Recherche les entrées dont le champ 'text' contient au moins un mot de la requête.
    Retourne une liste d'extraits (strings) à afficher.
    """
    # Tokenisation très simple : on sépare la requête en mots
    mots_query = [w.strip().lower() for w in query.split() if w.strip()]
    if not mots_query:
        return []

    results = []
    for entry in load_memory_entries():
        texte = entry.get("text", "")
        texte_lower = texte.lower()

        # Si l'un des mots de la requête figure dans le texte de la note, on l'ajoute
        if any(mot in texte_lower for mot in mots_query):
            # Vous pouvez choisir d'afficher tout le texte ou un extrait
            results.append(f"- [{entry.get('timestamp','')}] {texte}")

        if len(results) >= max_results:
            break

    return results
