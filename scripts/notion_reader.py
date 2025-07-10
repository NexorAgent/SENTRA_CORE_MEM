import os
import sys

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from notion_config import DATABASE_ID, NOTION_TOKEN

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_recent_logs(limit=5):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "page_size": limit,
        "sorts": [{"timestamp": "created_time", "direction": "descending"}],
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        print("❌ Erreur Notion :", res.status_code, res.text)
        return []

    data = res.json()
    entries = []
    for result in data["results"]:
        props = result["properties"]
        titre = (
            props["Titre"]["rich_text"][0]["plain_text"]
            if props["Titre"]["rich_text"]
            else "Sans titre"
        )
        cat = (
            [c["name"] for c in props["Catégorie"]["multi_select"]]
            if props["Catégorie"]["multi_select"]
            else []
        )
        status = (
            [s["name"] for s in props["Statut"]["multi_select"]]
            if props["Statut"]["multi_select"]
            else []
        )
        entries.append({"titre": titre, "catégorie": cat, "statut": status})

    return entries


def filter_logs(field="Catégorie", value="bim"):
    entries = get_recent_logs(limit=50)
    filtered = []
    for e in entries:
        if value in e.get(field.lower(), []):
            filtered.append(e)
    return filtered


# Test simple
if __name__ == "__main__":
    print("🧠 Derniers logs :")
    for log in get_recent_logs():
        print(log)
