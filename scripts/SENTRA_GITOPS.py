"""Outils Git simples pour SENTRA_CORE_MEM.

Usage :
    python SENTRA_GITOPS.py status|add|commit "message"|push
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_git(args: list[str]) -> subprocess.CompletedProcess:
    """Execute une commande git à la racine du projet."""
    return subprocess.run(
        ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True
    )


def get_current_branch() -> str:
    """Retourne le nom de la branche courante."""
    result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return result.stdout.strip()


def status_git() -> None:
    """Affiche la branche courante et les fichiers modifiés."""
    branch = get_current_branch()
    result = _run_git(["status", "--short"])
    print(f"Branch: {branch}")
    if result.stdout:
        print(result.stdout.strip())


def add_all() -> None:
    """Ajoute tous les fichiers modifiés à l'index."""
    _run_git(["add", "."])


def commit_changes(msg: str) -> None:
    """Crée un commit avec le message donné."""
    res = _run_git(["commit", "-m", msg])
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())


def push_changes() -> None:
    """Push la branche courante vers 'origin'."""
    branch = get_current_branch()
    res = _run_git(["push", "origin", branch])
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())


COMMANDS = {
    "status": status_git,
    "add": add_all,
    "commit": commit_changes,
    "push": push_changes,
}


def main(args: list[str]) -> None:
    if not args:
        print("Usage: python SENTRA_GITOPS.py status|add|commit \"message\"|push")
        return
    cmd = args[0]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        return
    if cmd == "commit":
        if len(args) < 2:
            print("Commit message required")
            return
        COMMANDS[cmd](args[1])
    else:
        COMMANDS[cmd]()


if __name__ == "__main__":
    main(sys.argv[1:])
