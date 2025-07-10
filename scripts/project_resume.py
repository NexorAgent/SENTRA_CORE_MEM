import sys
from datetime import datetime
from pathlib import Path

# Ce script génère un résumé basique du projet en listant les fichiers et extraits
# Usage: python project_resume.py <nom_du_projet>



def summarize_project(project_name: str):
    project_slug = project_name.lower().replace(" ", "_").replace("/", "_")
    base_path = Path("projects") / project_slug / "fichiers"
    if not base_path.exists():
        print(f"❌ Le dossier du projet n'existe pas : {base_path}")
        return

    # Fichier de sortie résumé
    resume_dir = Path("projects") / project_slug / "resume"
    resume_dir.mkdir(parents=True, exist_ok=True)
    resume_path = resume_dir / f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    lines = []
    lines.append(
        f"# Résumé du projet {project_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    # Lister tous les fichiers dans 'fichiers'
    lines.append("## Liste des fichiers disponibles :\n")
    for filepath in sorted(base_path.glob("*")):
        rel = filepath.relative_to(base_path.parent.parent)
        lines.append(f"- {rel} (taille: {filepath.stat().st_size} octets)\n")

    # Ajouter extrait des logs (premières lignes)
    log_files = sorted(base_path.glob("log_*.txt"))
    if log_files:
        lines.append("\n## Extraits des logs :\n")
        for log in log_files[-1:]:  # dernier log
            lines.append(f"### Contenu de {log.name}:\n```")
            try:
                with log.open("r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                        lines.append(line.rstrip())
            except Exception as e:
                lines.append(f"Erreur lecture log: {e}")
            lines.append("```\n")
    else:
        lines.append("\n_Aucun log disponible._\n")

    # Ajouter extrait des fichiers Markdown (premières lignes)
    md_files = sorted(base_path.glob("*.md"))
    if md_files:
        lines.append("## Extraits des fichiers Markdown :\n")
        for md in md_files:
            lines.append(f"### Contenu de {md.name}:\n```")
            try:
                with md.open("r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                        lines.append(line.rstrip())
            except Exception as e:
                lines.append(f"Erreur lecture MD: {e}")
            lines.append("```\n")
    else:
        lines.append("\n_Aucun fichier Markdown disponible._\n")

    # Écrire le résumé
    try:
        with resume_path.open("w", encoding="utf-8") as out:
            out.write("\n".join(lines))
        print(f"✅ Résumé généré: {resume_path}")
    except Exception as e:
        print(f"❌ Erreur écriture résumé: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python project_resume.py <nom_du_projet>")
        exit(1)
    summarize_project(sys.argv[1])
