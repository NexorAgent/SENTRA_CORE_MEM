import requests
import subprocess
import os
from datetime import datetime

print("🚀 Test 03 : lancement de la vérification Git après ajout mémoire")

try:
    # Config
    API_URL = "http://127.0.0.1:8000/write_note"
    project = "git_test_project"
    now = datetime.now().isoformat()
    note_text = "Note de test Git automatique - " + now
    print("📝 Contenu de la note :", note_text)

    # Payload
    payload = {
        "project": project,
        "text": note_text,
        "type": "note"
    }

    # Envoi
    response = requests.post(API_URL, json=payload)
    print(f"📡 Statut API : {response.status_code}")
    print(f"Réponse : {response.text}")

except Exception as e:
    print("❌ ERREUR détectée :", str(e))

# 2. Vérification d’un commit Git après ajout
try:
    result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
    last_commit_msg = result.stdout.strip()
    if project in last_commit_msg or note_text[:20] in last_commit_msg:
        print(f"✅ Commit Git détecté : {last_commit_msg}")
    else:
        print(f"⚠️ Dernier commit ne contient pas la note test : {last_commit_msg}")
except Exception as e:
    print(f"❌ Erreur vérification Git : {e}")
