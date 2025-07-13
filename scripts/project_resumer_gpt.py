#!/home/debian/venv_sentra/bin/python

import os
import zlib
import base64
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from packaging import version  # pour comparer les versions (optionnel ici)

# ————————————————
# 1. Configuration OpenAI
# ————————————————
def setup_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erreur : OPENAI_API_KEY non défini.")
        exit(1)
    return OpenAI(api_key=api_key)

# ————————————————
# 2. Compression glyphique
# ————————————————
def compress_to_glyph(text: str) -> str:
    compressed = zlib.compress(text.encode("utf-8"))
    b64 = base64.b64encode(compressed).decode("utf-8")
    return b64

# ————————————————
# 3. Appel à l’API via l’ancienne interface
# ————————————————
def summarize_with_gpt(client, compressed_content: str) -> str:
    prompt = (
        "Tu es une IA selon le serment SENTRA_OATH. "
        "Ci-dessous un contenu compressé (zlib+base64). "
        "1) Décode-le pour récupérer le texte brut. "
        "2) Résume le texte en français en 5 bullet points, hiérarchisés, économie de tokens. "
        "3) Mentionne les sources (titres de sections) dans le résumé.\n\n"
        f"Contenu glyphique : {compressed_content}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )

    return response.choices[0].message.content

# ————————————————
# 4. Fonction principale
# ————————————————
def main(project_name: str):
    # Trouver le dossier de résumé du projet
    project_slug = project_name.lower().replace(" ", "_")
    resume_folder = Path("projects") / project_slug / "resume"
    if not resume_folder.exists():
        print(f"❌ Pas de dossier resume pour le projet {project_name}.")
        exit(1)

    # Sélectionner le fichier résumé brut le plus récent
    resume_files = list(resume_folder.glob("resume_*.md"))
    if not resume_files:
        print(f"❌ Aucun fichier résumé trouvé dans {resume_folder}.")
        exit(1)
    latest_resume = max(resume_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Lecture du fichier résumé : {latest_resume}")

    # Lire le contenu brut du fichier
    content = latest_resume.read_text(encoding="utf-8")

    # Compression glyphique
    glyph = compress_to_glyph(content)
    print(f"🔢 Contenu compressé (longueur = {len(glyph)} chars)")

    # Configurer OpenAI et demander le résumé
    client = setup_openai()

    try:
       summary = summarize_with_gpt(client, glyph)

    except Exception as e:
        # Si ça plante, on affiche l’erreur et on termine avec un code non-zéro
        print(f"❌ Erreur OpenAI : {e}")
        exit(1)

    # Sauvegarder le résumé GPT dans un nouveau fichier
    output_folder = Path("projects") / project_slug / "resume"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_folder / f"resume_gpt_{timestamp}.md"
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write(summary)
        print(f"✅ Résumé GPT généré : {output_path}")
    except Exception as e:
        print(f"❌ Erreur écriture du résumé GPT : {e}")
        exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python project_resumer_gpt.py <nom_du_projet>")
        exit(1)
    main(sys.argv[1])
