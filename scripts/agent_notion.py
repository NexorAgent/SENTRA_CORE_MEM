# gpt/agent_notion.py

import os
import sys
import requests
from datetime import datetime

# ─────────────────────────────────────────────────────
# Ajouter la racine du projet à sys.path pour trouver markdown_generator, si besoin
# ─────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))            # .../SENTRA_CORE_MEM_merged/gpt
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))  # .../SENTRA_CORE_MEM_merged
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Lecture des variables d’environnement à la place de notion_config.py
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID  = os.getenv("NOTION_DB_ID")

# En-têtes pour l’API Notion
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def send_to_notion(name: str,
                   titre: str,
                   categorie: str = "mémoire",
                   statut: str = "À valider",
                   validation: str = "auto",
                   utilisation: str = "pro",
                   url: str = ""):
    """
    Crée une page dans la base Notion indiquée par DATABASE_ID.
    Les propriétés correspondent à votre schéma : Name, Titre, Date, Catégorie, Statut, Validation ZORAN, Utilisation, URL.
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        print("❌ Erreur : NOTION_TOKEN ou NOTION_DB_ID non défini.e.s.")
        return {"réponse": "Échec synchronisation : variables d'environnement manquantes", "glyph": "❌"}

    url_post = "https://api.notion.com/v1/pages"
    now_iso = datetime.now().isoformat()

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": name}}]},
            "Titre": {"rich_text": [{"text": {"content": titre}}]},
            "Date": {"date": {"start": now_iso}},
            "Catégorie": {"multi_select": [{"name": categorie}]},
            "Statut": {"multi_select": [{"name": statut}]},
            "Validation ZORAN": {"multi_select": [{"name": validation}]},
            "Utilisation": {"rich_text": [{"text": {"content": utilisation}}]},
            "URL": {"url": url}
        }
    }

    # Affichage des données envoyées pour debug (ASCII uniquement)
    print("[POST DATA]:", data)
    print("[HEADERS]:", headers)

    try:
        response = requests.post(url_post, headers=headers, json=data)
        print(f"[RESPONSE]: {response.status_code} {response.text}")
        if response.status_code not in (200, 201):
            return {"réponse": f"Erreur Notion : {response.status_code} {response.text}", "glyph": "❌"}
        return {"réponse": "Mémoire synchronisée dans Notion.", "glyph": "✔️ SYNC.NOTION"}
    except Exception as exc:
        print("❌ Exception Notion :", exc)
        return {"réponse": f"Exception Notion : {exc}", "glyph": "❌"}

def run():
    # Exemple de test : on envoie une page avec des valeurs par défaut.
    return send_to_notion(
        name="Test Mémoire",
        titre="Synchronisation de test",
        categorie="mémoire",
        statut="À valider",
        validation="auto",
        utilisation="pro",
        url="https://example.com"  # Remplacez par une URL pertinente si besoin.
    )

if __name__ == "__main__":
    result = run()
    # Affichage ASCII uniquement (sans emoji) pour éviter UnicodeEncodeError sur Windows
    reponse = result.get("réponse", "")
    glyph   = result.get("glyph", "")
    # Conserver uniquement les caractères ASCII dans glyph
    glyph_ascii = "".join(ch for ch in glyph if ord(ch) < 128)
    print("[Réponse] ", reponse)
    print("[Statut ] ", glyph_ascii if glyph_ascii else "[aucun glyph ASCII]")
