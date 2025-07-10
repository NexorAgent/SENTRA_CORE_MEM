from __future__ import annotations
import subprocess
from pathlib import Path
import os

def git_commit_push(files: list[Path], message: str) -> None:
    """Add files, commit and push to the remote repository, PROD SAFE."""
    repo_root = Path(__file__).resolve().parent.parent
    rel_files = [str(f.relative_to(repo_root)) for f in files if f.exists()]

    # 1. Config git user (évite erreur 128)
    try:
        subprocess.run(
            ["git", "config", "--global", "user.email", "sentra@localhost"],
            check=False, cwd=repo_root
        )
        subprocess.run(
            ["git", "config", "--global", "user.name", "SENTRA CORE BOT"],
            check=False, cwd=repo_root
        )
    except Exception as e:
        print(f"⚠️ Impossible de configurer git user: {e}")

    # 2. Tente add/commit/push, mais n'arrête jamais l'API si erreur
    try:
        subprocess.run(["git", "add", *rel_files], check=True, cwd=repo_root)
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=repo_root)
        subprocess.run(["git", "push"], check=True, cwd=repo_root)
        print("✅ Git commit/push réussi.")
    except subprocess.CalledProcessError as exc:
        print(f"⚠️ Git command failed: {exc}")
        # Sur Render on ne lève PAS d'exception bloquante
        # (option: log dans un fichier ou notifier si besoin)

    # 3. L’API ne bloque JAMAIS même si git échoue !
