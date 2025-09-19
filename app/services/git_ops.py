from __future__ import annotations

from datetime import datetime, timezone
import subprocess
from pathlib import Path
from typing import Optional


class GitOpsError(RuntimeError):
    """Raised when git operations fail."""


class GitOpsHelper:
    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def commit_and_push(self, tool: str, file_path: Path, agent: str, content_hash: str) -> Optional[str]:
        relative_path = file_path.relative_to(self._repo_root)
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"[{tool}] {relative_path} {content_hash} by {agent} {timestamp}"
        self._run(["git", "add", str(relative_path)])
        try:
            self._run(["git", "commit", "-m", message])
        except GitOpsError as error:
            if "nothing to commit" in str(error).lower():
                return None
            raise
        remote_output = self._run(["git", "remote"], capture_output=True)
        remote_names = [line.strip() for line in remote_output.splitlines() if line.strip()]
        if not remote_names:
            return message
        self._run(["git", "push"])
        return message

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
            raise GitOpsError(output or f"Command {' '.join(command)} failed")
        if capture_output:
            return result.stdout
        return ""
