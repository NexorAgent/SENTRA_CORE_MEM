# app/services/git_ops.py
from __future__ import annotations

from datetime import datetime, timezone
import subprocess
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

class GitOpsError(RuntimeError):
    """Raised when git operations fail."""
    def __init__(self, message: str, returncode: int | None = None) -> None:
        super().__init__(message)
        self.returncode = returncode

class GitOpsHelper:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        self._idempotency_cache: dict[str, Optional[str]] = {}

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    # --- helpers ---
    def _to_repo_rel(self, p: Union[str, Path]) -> str:
        p = Path(p)
        # si absolu, essaie de relativiser à la racine du repo
        try:
            return str(p.relative_to(self.repo_root).as_posix())
        except ValueError:
            # sinon, retire le slash de tête et normalise
            return str(p.as_posix().lstrip("/"))

    def _run(self, args: Sequence[str], cwd: Optional[Path] = None, capture_output: bool = True) -> str:
        result = subprocess.run(
            list(args),
            cwd=str(cwd or self.repo_root),
            capture_output=capture_output,
            text=True
        )
        stdout = (result.stdout or '').strip()
        stderr = (result.stderr or '').strip()
        if result.returncode != 0:
            # Utiliser GitOpsError pour que les appelants puissent l'attraper
            msg = stderr or stdout or f"Command failed: {' '.join(args)}"
            raise GitOpsError(msg, returncode=result.returncode)
        # Retourne le flux non vide (stdout en priorité)
        return stdout if stdout else stderr

    def _push(self) -> None:
        # s'il n'y a pas de remote, on sort proprement
        remotes = self._run(["git", "remote"], capture_output=True).splitlines()
        remotes = [r.strip() for r in remotes if r.strip()]
        if not remotes:
            return

        # branche courante
        branch = self._run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True).strip()

        try:
            # pousser HEAD sur une branche de même nom et définir l’upstream si besoin
            self._run(["git", "push", "-u", "origin", "HEAD"])
        except GitOpsError as error:
            if error.returncode == 128:
                # tentatives de rattrapage en cas de divergence
                try:
                    self._run(["git", "pull", "--rebase"])
                except GitOpsError:
                    self._run(["git", "fetch", "--all"])
                # re-push
                self._run(["git", "push", "-u", "origin", "HEAD"])
            else:
                raise

    # --- API publiques ---
    def commit_and_push(
        self,
        tool: str,
        file_path: Path,
        agent: str,
        content_hash: str,
        idempotency_key: str | None = None,
    ) -> Optional[str]:
        if idempotency_key and idempotency_key in self._idempotency_cache:
            return self._idempotency_cache[idempotency_key]
        relative_path = file_path.relative_to(self.repo_root)
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"[{tool}] {relative_path} {content_hash} by {agent} {timestamp}"
        self._run(["git", "add", str(relative_path)])
        committed = True
        try:
            self._run(["git", "commit", "-m", message])
        except GitOpsError as error:
            if "nothing to commit" in str(error).lower():
                committed = False
            else:
                raise
        if committed:
            self._push()
            if idempotency_key:
                self._idempotency_cache[idempotency_key] = message
            return message
        else:
            if idempotency_key:
                self._idempotency_cache[idempotency_key] = None
            return None

    def commit_paths(
        self,
        branch: str,
        paths: Sequence[Union[str, Path]],
        message: str,
        agent: str,
        idempotency_key: str | None = None,
    ) -> dict[str, Optional[str]]:
        if idempotency_key and idempotency_key in self._idempotency_cache:
            cached = self._idempotency_cache[idempotency_key]
            return {"committed": cached is not None, "sha": cached}

        if not paths:
            raise ValueError("Aucun chemin à committer")

        rel_paths = [self._to_repo_rel(p) for p in paths]
        self._run(["git", "checkout", branch])
        self._run(["git", "add"] + rel_paths)

        committed = True
        try:
            self._run(["git", "commit", "-m", message])
        except GitOpsError as error:
            if "nothing to commit" in str(error).lower():
                committed = False
            else:
                raise

        sha: Optional[str] = None
        if committed:
            sha = self._run(["git", "rev-parse", "HEAD"]).strip()
            self._push()

        if idempotency_key:
            self._idempotency_cache[idempotency_key] = sha
        return {"committed": committed, "sha": sha}
