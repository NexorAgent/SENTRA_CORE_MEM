#!/usr/bin/env python3
"""
agent_markdown.py — Générateur de rapport Markdown pour SENTRA_CORE_MEM
Usage:
    python agent_markdown.py YYYY-MM-DD  # appel direct en CLI
    ou
    run()                                 # appelé depuis le bot Discord
Crée un fichier reports/YYYY/MM/YYYY-MM-DD_rapport.md avec contenu basique.
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# Répertoire racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Répertoire des rapports
REPORTS_DIR = PROJECT_ROOT / "reports"

# Répertoire mémoire et logs
MEMORY_FILE = PROJECT_ROOT / "memory" / "sentra_memory.json"
LOG_FILE = PROJECT_ROOT / "logs" / "execution_log.txt"

def load_memory_entries():
    """Retourne la liste des entrées mémoire JSON."""
    if not MEMORY_FILE.exists():
        return []

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def load_logs_for_date(date_str):
    logs = []
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(f"[{date_str}"):
                        logs.append(line.strip())
        except Exception:
            pass
    return logs


def generate_markdown(date_str):
    # Créer le répertoire reports/YYYY/MM
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Format de date invalide: {date_str}. Utiliser YYYY-MM-DD.")

    year = date_obj.strftime("%Y")
    month = date_obj.strftime("%m")
    # day = date_obj.strftime("%d")  # non utilisé

    dir_path = REPORTS_DIR / year / month
    dir_path.mkdir(parents=True, exist_ok=True)

    file_name = f"{date_str}_rapport.md"
    file_path = dir_path / file_name

    # Contenu du rapport
    lines = []
    lines.append(f"# Rapport – {date_str}\n")

    # Section logs
    lines.append("## Logs\n")
    logs = load_logs_for_date(date_str)
    if logs:
        for log in logs:
            lines.append(f"- {log}\n")
    else:
        lines.append("_Aucun log pour cette date._\n")

    # Section mémoire
    lines.append("## Mémoire\n")
    entries = load_memory_entries()
    filtered = [e for e in entries if e.get("timestamp", "").startswith(date_str)]
    if filtered:
        for entry in filtered:
            text = entry.get("text", "")
            lines.append(f"- {text}\n")
    else:
        lines.append("_Aucune entrée mémoire pour cette date._\n")

    # Écrire le fichier
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(line if line.endswith("\n") else line + "\n" for line in lines)
    except Exception as e:
        raise IOError(f"Échec de l'écriture du rapport: {e}")

    return file_path


def run():
    # Génère le rapport pour la date courante
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        file_path = generate_markdown(date_str)
        # Retourner un dict que le bot utilisera
        return {"réponse": f"📄 Rapport généré: {file_path}"}
    except Exception as e:
        return {"réponse": f"❌ Erreur lors de la génération du rapport: {e}"}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python agent_markdown.py YYYY-MM-DD")
        sys.exit(1)
    try:
        file_path = generate_markdown(sys.argv[1])
        print(f"📄 Rapport généré: {file_path}")
    except Exception as e:
        print(e)
        sys.exit(1)
