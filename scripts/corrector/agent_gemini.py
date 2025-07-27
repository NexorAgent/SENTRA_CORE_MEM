import subprocess
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from scripts.core.prompt_pool_loader import load_prompt

def correct_with_gemini(file_path):
    """
    Utilise Gemini CLI pour corriger un fichier Python.
    Charge le prompt depuis YAML, insère le code, exécute Gemini CLI,
    et écrase le fichier d’origine avec le code corrigé.
    """
    if not os.path.exists(file_path):
        return False, f"❌ Fichier introuvable : {file_path}"

    try:
        with open(file_path, "r") as f:
            code = f.read().strip()

        # Chargement du prompt YAML
        prompt_data = load_prompt("corrector")
        prompt_template = prompt_data["prompt"]
        prompt = prompt_template.replace("{code}", code)

        # Appel Gemini CLI
        result = subprocess.run(
            ["gemini", "--prompt", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return False, f"❌ Erreur Gemini CLI : {result.stderr.strip()}"

        response = result.stdout.strip()

        # Tentative de parsing JSON
        try:
            import json
            parsed = json.loads(response)

            if "corrected_code" not in parsed or not parsed["corrected_code"].strip():
                return False, "❌ Réponse Gemini invalide : champ 'corrected_code' manquant ou vide."

            corrected_code = parsed["corrected_code"].strip()

        except Exception as e:
            return False, f"❌ Réponse Gemini non parseable en JSON : {str(e)}"

        # Écriture du fichier uniquement si tout est OKdef correct_with_gemini(file_path):
        with open(file_path, "w") as f:
            f.write(corrected_code)

        return True, "✅ Correction par Gemini CLI réussie."

    except Exception as e:
        return False, f"❌ Exception agent_gemini : {str(e)}"
