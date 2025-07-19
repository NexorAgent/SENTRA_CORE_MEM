#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Création autonome d'une structure de projet intelligent SENTRA
- Type : apprentissage, IA, Bim, Dev
- Génération dossier, README, script init, workflows n8n
"""
import os
from pathlib import Path

def create_project(project_name: str, categories: list[str] = []):
    base_path = Path("projects") / project_name
    subfolders = ["data", "scripts", "docs", "workflows", "models"] + categories
    for folder in subfolders:
        path = base_path / folder
        path.mkdir(parents=True, exist_ok=True)

    # Fichiers de base
    (base_path / "README.md").write_text(f"# Projet {project_name}\n\nStructure initialisée par SENTRA_CORE\n")
    (base_path / "scripts" / "main.py").write_text("""#!/usr/bin/env python3
# Main script du projet

if __name__ == '__main__':
    print('Hello from', __file__)
""")

    print(f"✅ Projet '{project_name}' créé avec succès !")

if __name__ == '__main__':
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "apprentissage-ia"
    cats = sys.argv[2:] if len(sys.argv) > 2 else ["ressources", "tests"]
    create_project(name, cats)