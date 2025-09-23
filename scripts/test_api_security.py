import pytest
from fastapi.testclient import TestClient

import scripts.api_sentra as api


@pytest.fixture
def client(tmp_path, monkeypatch):
    dummy = tmp_path / "scripts" / "api_sentra.py"
    dummy.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(api, "__file__", str(dummy))
    monkeypatch.setattr(api, "BASE_DIR", tmp_path)
    monkeypatch.setattr(api, "git_commit_push", lambda *args, **kwargs: None)
    return TestClient(api.app)


def test_write_file_rejects_absolute_path(client):
    response = client.post(
        "/write_file",
        json={"project": "demo", "filename": "/etc/passwd", "content": "x"},
    )
    assert response.status_code == 400


def test_write_file_rejects_traversal(client):
    response = client.post(
        "/write_file",
        json={"project": "demo", "filename": "../../secret", "content": "x"},
    )
    assert response.status_code == 400


def test_write_file_rejects_invalid_project_slug(client):
    response = client.post(
        "/write_file",
        json={"project": "../demo", "filename": "note.txt", "content": "x"},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"src": "/etc/passwd", "dst": "safe.txt"},
        {"src": "safe.txt", "dst": "../escape.txt"},
    ],
)
def test_move_file_rejects_out_of_base(client, payload):
    response = client.post("/move_file", json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {"path": "/etc/passwd", "archive_dir": "archive"},
        {"path": "projects/demo/file.txt", "archive_dir": "../../outside"},
    ],
)
def test_archive_file_rejects_invalid_paths(client, payload):
    response = client.post("/archive_file", json=payload)
    assert response.status_code == 400


def test_delete_file_rejects_traversal(client):
    response = client.post("/delete_file", json={"path": "../../secret"})
    assert response.status_code == 400


def test_get_memorial_rejects_invalid_project(client):
    response = client.get("/get_memorial", params={"project": "../"})
    assert response.status_code == 400


def test_list_files_rejects_invalid_dir(client):
    response = client.get("/list_files", params={"dir": "../../secret"})
    assert response.status_code == 400


def test_search_files_rejects_invalid_dir(client):
    response = client.get("/search", params={"term": "x", "dir": "../../secret"})
    assert response.status_code == 400


def test_read_note_rejects_invalid_filepath(client):
    response = client.get("/read_note", params={"filepath": "../../secret"})
    assert response.status_code == 400
