import os
import zlib
import base64
import openai
from pathlib import Path
from datetime import datetime
from packaging import version  # pour comparer les versions

# ————————————————
# 1. Configuration OpenAI
# ————————————————
def setup_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Erreur : OPENAI_API_KEY non défini.")
        exit(1)
    openai.api_key = api_key

# ————————————————
# 2. Compression glyphique
# ————————————————
def compress_to_glyph(text: str) -> str:
    compressed = zlib.compress(text.encode("utf-8"))
    b64 = base64.b64encode(compressed).decode("utf-8")
    return b64

# ————————————————
# 3. Appel à l’API (interface adaptée selon la version du SDK)
# ————————————————
def summarize_with_gpt(compressed_content: str) -> str:
    prompt = (
        "Tu es une IA selon le serment SENTRA_OATH. "
        "Ci-dessous un contenu compressé (zlib+base64). "
        "1) Décode-le pour récupérer le texte brut. "
        "2) Résume le texte en français en 5 bullet points, hiérarchisés, économie de tokens. "
        "3) Mentionne les sources (titres de sections) dans le résumé.\n\n"
        f"Contenu glyphique : {compressed_content}\n"
    )

    # On ne passe PAS l’argument 'proxies' au client OpenAI
    oi_version = version.parse(openai.__version__)
    if oi_version >= version.parse("1.0.0"):
        # Nouvelle interface pour openai >= 1.0.0
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    else:
        # Ancienne interface pour openai < 1.0.0
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message["content"]

# ————————————————
# 4. Fonction principale
# ————————————————
def main(project_name: str):
    # Trouver le dossier de résumé du projet
    project_slug = project_name.lower().replace(" ", "_")
    resume_folder = Path("projects") / project_slug / "resume"
    if not resume_folder.exists():
        print(f"❌ Pas de dossier resume pour le projet {project_name}.")
        return

    # Sélectionner le fichier résumé brut le plus récent
    resume_files = list(resume_folder.glob("resume_*.md"))
    if not resume_files:
        print(f"❌ Aucun fichier résumé trouvé dans {resume_folder}.")
        return
    latest_resume = max(resume_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Lecture du fichier résumé : {latest_resume}")

    # Lire le contenu brut du fichier
    try:
        content = latest_resume.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Impossible de lire le fichier résumé : {e}")
        return

    # Compression glyphique
    glyph = compress_to_glyph(content)
    print(f"🔢 Contenu compressé (longueur = {len(glyph)} chars)")

    # Configurer OpenAI et demander le résumé
    setup_openai()
    # Si OpenAI plante, on laisse l’exception remonter afin que l’API /reprise puisse renvoyer une erreur
    summary = summarize_with_gpt(glyph)

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python project_resumer_gpt.py <nom_du_projet>")
        exit(1)
    main(sys.argv[1])
