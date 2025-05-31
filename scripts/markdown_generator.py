import os
from datetime import datetime
from configs.config import CONFIG  # Chemin mis à jour

def generate_markdown(memory_content, title="Mémoire IA/IA"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = f"# {title}\n\n"
    md += f"**Généré le :** {timestamp}\n\n"
    md += "## Contenu compressé :\n"
    md += f"```text\n{memory_content}\n```\n"
    return md

if __name__ == "__main__":
    mem_path = "memories/example.zmem.src"
    if not os.path.exists(mem_path):
        print(f"❌ Fichier mémoire non trouvé : {mem_path}")
        exit(1)

    with open(mem_path, "r", encoding="utf-8") as f:
        content = f.read()

    markdown = generate_markdown(content, title="Mémoire IA/IA")
    output_path = "docs/memoire_generee.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Markdown généré : {output_path}")
