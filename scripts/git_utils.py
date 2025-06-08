from __future__ import annotations
import subprocess
from pathlib import Path


def git_commit_push(files: list[Path], message: str) -> None:
    """Add files, commit and push to the remote repository."""
    repo_root = Path(__file__).resolve().parent.parent
    rel_files = [str(f.relative_to(repo_root)) for f in files if f.exists()]
    try:
        subprocess.run(["git", "add", *rel_files], check=True, cwd=repo_root)
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=repo_root)
        subprocess.run(["git", "push"], check=True, cwd=repo_root)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Git command failed: {exc}")
