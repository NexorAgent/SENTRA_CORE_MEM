import requests

# Tester le endpoint /write_note de l'API SENTRA_CORE_MEM
payload = {
    "project": "test_project",
    "text": "Ceci est une note de test pour la mémoire persistante.",
    "type": "note"
}

response = requests.post("http://127.0.0.1:8000/write_note", json=payload)

if response.status_code == 200:
    print("✅ Test écriture mémoire réussi.")
    print(response.json())
else:
    print("❌ Échec de l'écriture mémoire.")
    print("Code:", response.status_code)
    print("Réponse:", response.text)
