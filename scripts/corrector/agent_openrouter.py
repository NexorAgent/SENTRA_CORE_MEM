import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Pour accéder au prompt YAML
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.core.prompt_pool_loader import load_prompt

def correct_with_openrouter(file_path, model="agentica-org/deepcoder-14b-preview"):
    """
    Utilise OpenRouter (via SDK OpenAI) pour corriger un fichier Python.
    Attend une réponse JSON avec champ 'corrected_code'.
    """
    if not os.path.exists(file_path):
        return False, f"❌ Fichier introuvable : {file_path}"

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False, "❌ OPENROUTER_API_KEY non défini."

    try:
        with open(file_path, "r") as f:
            code = f.read().strip()

        # Charger prompt depuis YAML
        prompt_data = load_prompt("corrector")
        prompt_template = prompt_data.get("prompt", "")
        prompt = prompt_template.replace("{code}", code)

        # Configuration OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un agent expert de correction de code dans le projet SENTRA_CORE_MEM."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://sentra.local",
                "X-Title": "SENTRA_CORRECTOR++"
            }
        )

        raw = response.choices[0].message.content.strip()
        with open("logs/last_raw_openrouter.txt", "w") as f:
            f.write(raw)

        # Nettoyage des blocs Markdown ```json, ```python, etc.
        if raw.startswith("```"):
            raw = raw.lstrip("`").split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0].strip()

        try:
            parsed = json.loads(raw)
            corrected = parsed.get("corrected_code", "").strip()

            if not corrected:
                return False, "❌ Réponse JSON reçue, mais champ 'corrected_code' vide."

            with open(file_path, "w") as f:
                f.write(corrected)

            return True, "✅ Correction OpenRouter réussie."

        except Exception as e:
            return False, f"❌ Réponse non JSON : {raw[:500]}..."

    except Exception as e:
        return False, f"❌ Exception OpenRouter : {str(e)}"
