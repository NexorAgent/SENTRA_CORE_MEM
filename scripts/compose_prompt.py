import openai
import json
import sys
import zlib
import base64
import os

# Chargement de la config
with open("configs/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

# Chargement de la clé API depuis l’environnement
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("❌ Clé OpenAI manquante. Définis OPENAI_API_KEY dans ton environnement.")

# Fonction exportable : permet d’utiliser ce script comme module
def load_memory_and_ask(project="test_project", question="Que contient cette mémoire ?"):
    zmem_path = f"memories/{project}.zmem"
    if not os.path.exists(zmem_path):
        raise FileNotFoundError(f"❌ Fichier {zmem_path} introuvable.")

    with open(zmem_path, "rb") as f:
        z = zlib.decompress(base64.b64decode(f.read())).decode("utf-8")

    messages = [
        {"role": "system", "content": z},
        {"role": "user", "content": question}
    ]

    response = openai.ChatCompletion.create(
        model=cfg.get("model", "gpt-4"),
        messages=messages,
        temperature=cfg.get("temperature", 0.5),
        max_tokens=cfg.get("max_tokens", 2048)
    )

    return response["choices"][0]["message"]["content"]

# Exécution directe depuis le terminal
if __name__ == "__main__":
    ctx = sys.argv[1] if len(sys.argv) > 1 else "test_project"
    try:
        result = load_memory_and_ask(project=ctx)
        print("✅ Réponse GPT :")
        print(result)
    except Exception as e:
        print(f"❌ Erreur : {e}")
