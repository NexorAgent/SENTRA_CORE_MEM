#!/usr/bin/env python3
import datetime
import json
import pathlib

# ─── Configuration ─────────────────────────────────────────────
# Définit la racine du projet (un niveau au-dessus de ce fichier)
ROOT = pathlib.Path(__file__).resolve().parents[1]
MEM_PATH = ROOT / "memory" / "sentra_memory.json"

# ─── Fonctions de gestion de la mémoire persistante ──────────────


def append_memory(contenu: str, typ: str = "log") -> None:
    """
    Ajoute une entrée dans le fichier de mémoire (format liste JSON).
    """
    # Crée le dossier si besoin
    MEM_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Charger la mémoire existante (ou init vide)
    if MEM_PATH.exists():
        try:
            with MEM_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    # Ajouter la nouvelle entrée
    data.append(
        {"date": datetime.date.today().isoformat(), "type": typ, "contenu": contenu}
    )

    # Réécriture complète
    with MEM_PATH.open("w", encoding="utf-8") as f:
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
