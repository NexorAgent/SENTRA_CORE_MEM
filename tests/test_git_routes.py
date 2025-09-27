from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_git_commit_push_returns_sha(client: TestClient, api_context: dict[str, object]) -> None:
    base_dir = api_context["base_dir"]  # type: ignore[index]
    target = Path(base_dir) / "projects" / "demo" / "notes" / "commit.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("note", encoding="utf-8")

    response = client.post(
        "/git/commitPush",
        json={
            "user": "ops",
            "agent": "scribe",
            "branch": "main",
            "paths": ["/projects/demo/notes/commit.md"],
            "message": "feat: commit depuis MCP",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["branch"] == "main"
    assert body["committed"] is True
    assert body["sha"].startswith("dummy-")


def test_git_commit_push_requires_paths(client: TestClient) -> None:
    response = client.post(
        "/git/commitPush",
        json={
            "user": "ops",
            "agent": "scribe",
            "branch": "main",
            "paths": [],
            "message": "noop",
        },
    )
    assert response.status_code == 422
