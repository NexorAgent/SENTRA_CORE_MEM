import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import scripts.api_sentra as api


@pytest.fixture
def client(tmp_path, monkeypatch):
    dummy = tmp_path / "scripts" / "api_sentra.py"
    dummy.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(api, "__file__", str(dummy))
    monkeypatch.setattr(api, "git_commit_push", lambda *a, **k: None)
    return TestClient(api.app)


def test_write_note_success(client, tmp_path):
    resp = client.post("/write_note", json={"text": "hello", "project": "demo"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    mem_file = tmp_path / "memory" / "sentra_memory.json"
    assert mem_file.exists()
    notes = json.loads(mem_file.read_text())
    assert notes[-1]["text"] == "hello"
    proj_file = tmp_path / "projects" / "demo" / "fichiers" / "memoire_demo.md"
    assert proj_file.exists()


def test_write_note_invalid(client):
    resp = client.post("/write_note", json={"text": "   "})
    assert resp.status_code == 400


def test_write_note_permission_error(client, monkeypatch):
    def fail(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr(Path, "write_text", fail)
    resp = client.post("/write_note", json={"text": "x"})
    assert resp.status_code == 500


def test_write_file_success(client, tmp_path):
    resp = client.post(
        "/write_file",
        json={"project": "demo", "filename": "a.txt", "content": "data"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    out = tmp_path / "projects" / "demo" / "fichiers" / "a.txt"
    assert out.exists()


def test_write_file_invalid(client):
    resp = client.post("/write_file", json={"project": "", "filename": "f", "content": "x"})
    assert resp.status_code == 400


def test_write_file_permission_error(client, monkeypatch):
    def fail(*args, **kwargs):
        raise PermissionError("no")
    monkeypatch.setattr(Path, "write_text", fail)
    resp = client.post(
        "/write_file",
        json={"project": "demo", "filename": "x.txt", "content": "x"},
    )
    assert resp.json()["status"] == "error"


def test_delete_file_success(client, tmp_path):
    base = tmp_path / "projects" / "demo" / "fichiers"
    base.mkdir(parents=True)
    f = base / "t.txt"
    f.write_text("ok")
    resp = client.post("/delete_file", json={"project": "demo", "filename": "t.txt"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert not f.exists()


def test_delete_file_not_found(client):
    resp = client.post("/delete_file", json={"project": "demo", "filename": "no.txt"})
    assert resp.json()["status"] == "error"


def test_delete_file_invalid(client):
    resp = client.post("/delete_file", json={"project": "", "filename": "f"})
    assert resp.status_code == 400


def test_move_file_success(client, tmp_path):
    base = tmp_path / "projects" / "demo" / "fichiers"
    base.mkdir(parents=True)
    src = base / "src.txt"
    src.write_text("data")
    resp = client.post(
        "/move_file",
        json={"project": "demo", "src": "src.txt", "dst": "dst.txt"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert not src.exists()
    assert (base / "dst.txt").exists()


def test_move_file_invalid(client):
    resp = client.post("/move_file", json={"project": "demo", "src": "a", "dst": ""})
    assert resp.status_code == 400


def test_archive_file_success(client, tmp_path):
    base = tmp_path / "projects" / "demo" / "fichiers"
    base.mkdir(parents=True)
    src = base / "arch.txt"
    src.write_text("data")
    resp = client.post(
        "/archive_file",
        json={"project": "demo", "filename": "arch.txt"},
    )
    assert resp.status_code == 200
    arc = tmp_path / "archive" / "demo" / "arch.txt"
    assert resp.json()["status"] == "success"
    assert arc.exists() and not src.exists()


def test_archive_file_invalid(client):
    resp = client.post("/archive_file", json={"project": "", "filename": "x"})
    assert resp.status_code == 400
