import os
import requests
import json

print("🚀 Test 04 : vérification webhook Discord /memoire")

# Lire le webhook depuis les variables d’environnement
webhook_url = os.getenv("WEBHOOK_URL")

if not webhook_url:
    print("❌ WEBHOOK_URL introuvable dans l’environnement Windows.")
    print("👉 Ajoute-le avec : setx WEBHOOK_URL \"https://discord.com/api/webhooks/...\"")
    exit(1)

# Contenu du message Discord simulé
payload = {
    "content": "/memoire SENTRA",
    "username": "SENTRA_TestBot"
}

# Envoi réel
try:
    r = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    if r.status_code == 204:
        print("✅ Message envoyé avec succès (204 No Content)")
    elif r.status_code == 200:
        print("✅ Message accepté (200 OK)")
    else:
        print(f"⚠️ Réponse Discord inattendue : {r.status_code}")
        print("Contenu :", r.text)
except Exception as e:
    print(f"❌ Erreur lors de l’envoi Discord : {e}")
