#!/usr/bin/env python3
import json
import datetime
import pathlib

# ─── Configuration ─────────────────────────────────────────────
# Définit la racine du projet (deux niveaux au-dessus de ce fichier)
ROOT = pathlib.Path(__file__).resolve().parents[2]
MEM_PATH = ROOT / "memory" / "sentra_memory.json"

# ─── Fonctions de gestion de la mémoire persistante ──────────────

def append_memory(contenu: str, typ: str = "log") -> None:
    """
    Ajoute une entrée dans le fichier de mémoire.
    """
    # Crée le dossier si besoin
    MEM_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Initialise le fichier si inexistant
    if not MEM_PATH.exists():
        MEM_PATH.write_text("[]", encoding="utf-8")

    # Charge, modifie et sauvegarde
    with MEM_PATH.open("r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append({
            "date": datetime.date.today().isoformat(),
            "type": typ,
            "contenu": contenu
        })
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()


def query_memory(limit: int = 5) -> list:
    """
    Renvoie les `limit` dernières entrées de la mémoire.
    """
    if not MEM_PATH.exists():
        return []
    with MEM_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return data[-limit:]


def search_memory(keyword: str) -> list:
    """
    Recherche les entrées contenant `keyword` (insensible à la casse).
    """
    if not MEM_PATH.exists():
        return []
    with MEM_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return [entry for entry in data if keyword.lower() in entry["contenu"].lower()]
