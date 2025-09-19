from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable


def _format_command(args: Iterable[str]) -> str:
    return " ".join(str(a) for a in args)


def git_commit_push(files: list[Path], message: str) -> None:
    """Add files, commit and push to the remote repository, PROD SAFE.

    Raises:
        RuntimeError: If a provided path is invalid or a git command fails.
    """
    repo_root = Path(__file__).resolve().parent.parent

    if not files:
        raise RuntimeError("Aucun fichier fourni pour git_commit_push.")

    normalized: list[tuple[Path, str]] = []
    for raw in files:
        if raw is None:
            raise RuntimeError("Un chemin None a été fourni à git_commit_push.")
        try:
            candidate = Path(raw)
        except TypeError as exc:
            raise RuntimeError(f"Chemin invalide fourni à git_commit_push: {raw!r}") from exc

        if not candidate.is_absolute():
            candidate = repo_root / candidate

        resolved = candidate.resolve(strict=False)

        try:
            relative = resolved.relative_to(repo_root)
        except ValueError as exc:
            raise RuntimeError(f"Chemin hors du dépôt refusé: {candidate}") from exc

        if relative == Path('.'):
            raise RuntimeError("Le dépôt complet ne peut pas être fourni à git_commit_push.")

        normalized.append((resolved, relative.as_posix()))

    if not normalized:
        raise RuntimeError("Aucun chemin valide n'a été fourni à git_commit_push.")

    seen: set[str] = set()
    existing: list[str] = []
    missing: list[str] = []

    for resolved, rel in normalized:
        if rel in seen:
            continue
        seen.add(rel)
        if resolved.exists():
            existing.append(rel)
        else:
            missing.append(rel)

    def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                args,
                cwd=repo_root,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover - handled via raise
            output = (exc.stderr or exc.stdout or "").strip()
            cmd = _format_command(args)
            detail = f": {output}" if output else ""
            raise RuntimeError(f"Commande git '{cmd}' échouée{detail}") from exc
        except OSError as exc:  # pragma: no cover - system level failure
            cmd = _format_command(args)
            raise RuntimeError(f"Échec d'exécution de '{cmd}': {exc}") from exc

    # 1. Config git user (évite erreur 128)
    try:
        run_git(["git", "config", "--global", "user.email", "sentra@localhost"], check=False)
        run_git(["git", "config", "--global", "user.name", "SENTRA CORE BOT"], check=False)
    except RuntimeError as e:
        print(f"⚠️ Impossible de configurer git user: {e}")

    if existing:
        run_git(["git", "add", "--", *existing])

    tracked_missing: list[str] = []
    for rel in missing:
        result = run_git(["git", "ls-files", "--error-unmatch", rel], check=False)
        if result.returncode == 0:
            tracked_missing.append(rel)

    if tracked_missing:
        run_git(["git", "add", "--update", "--", *tracked_missing])
        status = run_git(["git", "status", "--short"])
        status_lines = status.stdout.splitlines()

        def paths_from_status(line: str) -> list[str]:
            entry = line[3:] if len(line) > 3 else ""
            if " -> " in entry:
                old, new = entry.split(" -> ", 1)
                return [old, new]
            return [entry]

        for rel in tracked_missing:
            if not any(rel == path for line in status_lines for path in paths_from_status(line)):
                raise RuntimeError(
                    f"La suppression de {rel} n'est pas détectée par git status après staging."
                )

    # 2. Add/commit/push et lever une erreur claire en cas d'échec
    run_git(["git", "commit", "-m", message])
    run_git(["git", "push"])
    print("✅ Git commit/push réussi.")
