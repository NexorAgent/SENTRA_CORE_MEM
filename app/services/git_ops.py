from __future__ import annotations

from datetime import datetime, timezone
import subprocess
from pathlib import Path
from typing import Optional


class GitOpsError(RuntimeError):
    """Raised when git operations fail."""

    def __init__(self, message: str, returncode: int | None = None) -> None:
        super().__init__(message)
        self.returncode = returncode


class GitOpsHelper:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        self._idempotency_cache: dict[str, Optional[str]] = {}

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
        relative_path = file_path.relative_to(self._repo_root)
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"[{tool}] {relative_path} {content_hash} by {agent} {timestamp}"
        self._run(["git", "add", str(relative_path)])
        try:
            self._run(["git", "commit", "-m", message])
        except GitOpsError as error:
            if "nothing to commit" in str(error).lower():
                if idempotency_key:
                    self._idempotency_cache[idempotency_key] = None
                return None
            raise
        remote_output = self._run(["git", "remote"], capture_output=True)
        remote_names = [line.strip() for line in remote_output.splitlines() if line.strip()]
        commit_message: Optional[str] = message
        if remote_names:
            try:
                self._run(["git", "push"])
            except GitOpsError as error:
                if error.returncode == 128:
                    try:
                        self._run(["git", "pull", "--rebase"])
                    except GitOpsError:
                        self._run(["git", "fetch", "--all"])
                    self._run(["git", "push"])
                else:
                    raise
        if idempotency_key:
            self._idempotency_cache[idempotency_key] = commit_message
        return commit_message

    def _run(self, command: list[str], capture_output: bool = False) -> str:
        result = subprocess.run(
            command,
            cwd=self._repo_root,
            check=False,
            capture_output=capture_output,
            text=True,
        )
        if result.returncode != 0:
            output = result.stderr.strip() or result.stdout.strip()
            raise GitOpsError(output or f"Command {' '.join(command)} failed", returncode=result.returncode)
        if capture_output:
            return result.stdout
        return ""
