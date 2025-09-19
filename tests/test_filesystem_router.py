from __future__ import annotations

from pathlib import Path

import pytest


def test_write_file_success(client, api_context):
    response = client.post(
        "/write_file",
        json={"project": "Demo", "filename": "notes/spec.md", "content": "# Spec"},
    )
    assert response.status_code == 200
    data = response.json()
    written_path = Path(data["path"])
    expected_path = api_context["base_dir"] / "projects" / "demo" / "fichiers" / "notes" / "spec.md"
    assert written_path == expected_path
    assert written_path.read_text(encoding="utf-8") == "# Spec"
    assert any("GPT file update" in entry["message"] for entry in api_context["commits"])


def test_write_file_validation_errors(client):
    response = client.post(
        "/write_file",
        json={"project": "demo", "filename": " ", "content": "data"},
    )
    assert response.status_code == 400


def test_write_file_rejects_escape(client):
    response = client.post(
        "/write_file",
        json={"project": "demo", "filename": "../escape.md", "content": "no"},
    )
    assert response.status_code == 400


def test_move_file_success(client, api_context):
    base_dir = api_context["base_dir"]
    src_rel = Path("projects/demo/fichiers/spec.txt")
    dst_rel = Path("projects/demo/fichiers/spec-final.txt")
    src_path = base_dir / src_rel
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text("content", encoding="utf-8")

    response = client.post("/move_file", json={"src": str(src_rel), "dst": str(dst_rel)})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert not src_path.exists()
    assert (base_dir / dst_rel).exists()
    assert any("GPT move" in entry["message"] for entry in api_context["commits"])


def test_move_file_missing_source(client):
    response = client.post(
        "/move_file",
        json={
            "src": "projects/demo/fichiers/missing.txt",
            "dst": "projects/demo/fichiers/new-name.txt",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "introuvable" in data["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"src": " ", "dst": "projects/demo/fichiers/out.txt"},
        {"src": "projects/demo/fichiers/in.txt", "dst": ""},
    ],
)
def test_move_file_validation(payload, client):
    response = client.post("/move_file", json=payload)
    assert response.status_code == 400


def test_archive_file_success(client, api_context):
    base_dir = api_context["base_dir"]
    src_rel = Path("projects/demo/fichiers/archive.txt")
    archive_rel = Path("archive/demo")
    src_path = base_dir / src_rel
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text("archive me", encoding="utf-8")

    response = client.post(
        "/archive_file",
        json={"path": str(src_rel), "archive_dir": str(archive_rel)},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    dest_path = base_dir / archive_rel / src_path.name
    assert dest_path.exists() and not src_path.exists()
    assert any("GPT archive" in entry["message"] for entry in api_context["commits"])


@pytest.mark.parametrize(
    "payload",
    [
        {"path": " ", "archive_dir": "archive/demo"},
        {"path": "projects/demo/fichiers/file.txt", "archive_dir": "../escape"},
    ],
)
def test_archive_file_validation(client, payload):
    response = client.post("/archive_file", json=payload)
    assert response.status_code == 400


def test_delete_file_success(client, api_context):
    base_dir = api_context["base_dir"]
    file_rel = Path("projects/demo/fichiers/remove.txt")
    target = base_dir / file_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("bye", encoding="utf-8")

    response = client.post("/delete_file", json={"path": str(file_rel)})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert not target.exists()
    assert any("GPT delete" in entry["message"] for entry in api_context["commits"])


def test_delete_file_missing(client):
    response = client.post(
        "/delete_file",
        json={"path": "projects/demo/fichiers/ghost.txt"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "introuvable" in data["detail"]


def test_delete_file_validation(client):
    response = client.post("/delete_file", json={"path": " "})
    assert response.status_code == 400


def test_list_files_returns_matches(client, api_context):
    base_dir = api_context["base_dir"]
    project_dir = base_dir / "projects" / "demo" / "fichiers"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "a.md").write_text("A", encoding="utf-8")
    (project_dir / "b.txt").write_text("B", encoding="utf-8")

    response = client.get(
        "/list_files",
        params={"dir": "projects/demo/fichiers", "pattern": "*.md"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert str(project_dir / "a.md") in data["files"]
    assert str(project_dir / "b.txt") not in data["files"]


def test_search_files(client, api_context):
    base_dir = api_context["base_dir"]
    project_dir = base_dir / "projects" / "demo" / "fichiers"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "spec.md").write_text("Important spec for SENTRA", encoding="utf-8")

    response = client.get(
        "/search",
        params={"term": "spec", "dir": "projects/demo/fichiers"},
    )
    assert response.status_code == 200
    results = response.json()
    assert results["matches"]
    assert str(project_dir / "spec.md") in results["matches"]


def test_search_files_missing_directory(client):
    response = client.get(
        "/search",
        params={"term": "x", "dir": "projects/demo/missing"},
    )
    assert response.status_code == 404


def test_explore_prevents_escape(client):
    response = client.get(
        "/explore",
        params={"project": "demo", "path": "../../etc"},
    )
    assert response.status_code == 400


def test_explore_lists_files(client, api_context):
    base_dir = api_context["base_dir"]
    root = base_dir / "projects" / "demo"
    nested = root / "fichiers"
    nested.mkdir(parents=True, exist_ok=True)
    (nested / "index.md").write_text("content", encoding="utf-8")

    response = client.get(
        "/explore",
        params={"project": "demo", "path": "/"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["children"]
    assert any(item["name"] == "fichiers" for item in payload["children"])
