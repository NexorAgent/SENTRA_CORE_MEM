from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


def _write_payload(path: str, content: str) -> dict[str, str]:
    return {
        "path": path,
        "content": content,
        "user": "operator",
        "agent": "scribe",
    }


def test_files_write_creates_file_and_commits(client, api_context):
    response = client.post("/files/write", json=_write_payload("/projects/demo/docs/spec.md", "# Spec"))
    assert response.status_code == 200
    payload = response.json()
    written_path = Path(payload["path"])

    assert written_path.exists()
    assert written_path.read_text(encoding="utf-8") == "# Spec"

    expected_hash = hashlib.sha256("# Spec".encode("utf-8")).hexdigest()
    assert payload["sha256"] == expected_hash
    assert payload["committed"] is True
    assert payload["commit_message"] is not None

    assert any(commit["file"] == written_path for commit in api_context["git_commits"])
    assert any(event["tool"] == "files.write" for event in api_context["audit_events"])


def test_files_write_idempotent_when_content_unchanged(client, api_context):
    path = "/projects/demo/docs/spec.md"
    client.post("/files/write", json=_write_payload(path, "content"))
    commit_count = len(api_context["git_commits"])

    second = client.post("/files/write", json=_write_payload(path, "content"))
    assert second.status_code == 200
    body = second.json()
    assert body["committed"] is False
    assert body["commit_message"] is None
    assert len(api_context["git_commits"]) == commit_count


@pytest.mark.parametrize(
    "path_value",
    ["/unknown/root/file.txt", "/projects/../etc/passwd", "projects/demo/../../escape"],
)
def test_files_write_rejects_invalid_paths(client, path_value):
    response = client.post("/files/write", json=_write_payload(path_value, "data"))
    assert response.status_code == 400


def test_files_read_returns_content_and_metadata(client, api_context):
    target = api_context["base_dir"] / "projects" / "demo" / "docs" / "spec.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("spec content", encoding="utf-8")

    response = client.post("/files/read", json={"path": "/projects/demo/docs/spec.md", "user": "operator"})
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == str(target)
    assert data["content"] == "spec content"
    assert data["sha256"] == hashlib.sha256("spec content".encode("utf-8")).hexdigest()
    assert data["last_modified"] is not None


def test_files_read_missing_file_returns_404(client):
    response = client.post("/files/read", json={"path": "/projects/demo/missing.md", "user": "operator"})
    assert response.status_code == 404
