from __future__ import annotations

from app.services.git_ops import GitOpsError, GitOpsHelper


def test_commit_and_push_retries_after_pull(tmp_path, monkeypatch):
    repo_root = tmp_path
    helper = GitOpsHelper(repo_root)
    file_path = repo_root / "example.txt"
    file_path.write_text("content", encoding="utf-8")

    commands: list[list[str]] = []
    push_attempts = {"count": 0}

    def fake_run(command: list[str], capture_output: bool = False) -> str:
        commands.append(command)
        if command[:2] == ["git", "add"]:
            return ""
        if command[:2] == ["git", "commit"]:
            return ""
        if command[:2] == ["git", "remote"]:
            return "origin\n" if capture_output else ""
        if command[:3] == ["git", "pull", "--rebase"]:
            return ""
        if command[:2] == ["git", "fetch"]:
            return ""
        if command[:4] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
            return "main\n" if capture_output else ""
        if command[:2] == ["git", "push"]:
            push_attempts["count"] += 1
            if push_attempts["count"] == 1:
                raise GitOpsError("fatal: remote rejected", returncode=128)
            return ""
        raise AssertionError(f"Unexpected git command: {command}")

    monkeypatch.setattr(helper, "_run", fake_run)

    message = helper.commit_and_push("tool", file_path, "agent", "hash")

    assert push_attempts["count"] == 2
    assert ["git", "pull", "--rebase"] in commands or ["git", "fetch", "--all"] in commands
    assert message is not None
    assert "[tool]" in message


def test_commit_and_push_short_circuits_with_idempotency(tmp_path, monkeypatch):
    repo_root = tmp_path
    helper = GitOpsHelper(repo_root)
    file_path = repo_root / "another.txt"
    file_path.write_text("content", encoding="utf-8")

    commands: list[list[str]] = []

    def fake_run(command: list[str], capture_output: bool = False) -> str:
        commands.append(command)
        if command[:2] == ["git", "add"]:
            return ""
        if command[:2] == ["git", "commit"]:
            return ""
        if command[:4] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
            return "main\n" if capture_output else ""
        if command[:2] == ["git", "remote"]:
            return ""
        raise AssertionError(f"Unexpected git command: {command}")

    monkeypatch.setattr(helper, "_run", fake_run)

    first_message = helper.commit_and_push("tool", file_path, "agent", "hash", idempotency_key="abc")
    command_count = len(commands)

    second_message = helper.commit_and_push("tool", file_path, "agent", "hash", idempotency_key="abc")

    assert len(commands) == command_count
    assert second_message == first_message
