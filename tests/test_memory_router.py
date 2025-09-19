from __future__ import annotations

import json
from pathlib import Path


def test_write_note_persists_and_logs(client, api_context):
    response = client.post(
        "/write_note",
        json={"text": "Capture meeting notes", "project": "Demo"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"

    base_dir = api_context["base_dir"]
    mem_file = base_dir / "memory" / "sentra_memory.json"
    assert mem_file.exists()
    entries = json.loads(mem_file.read_text(encoding="utf-8"))
    assert entries[-1]["text"] == "Capture meeting notes"

    memorial = base_dir / "projects" / "demo" / "fichiers" / "Z_MEMORIAL.md"
    assert memorial.exists()
    memorial_content = memorial.read_text(encoding="utf-8")
    assert "Capture meeting notes" in memorial_content

    assert any("GPT note" in entry["message"] for entry in api_context["commits"])


def test_write_note_requires_non_empty_text(client):
    response = client.post("/write_note", json={"text": "  "})
    assert response.status_code == 400


def test_get_memorial_returns_placeholder(client):
    response = client.get("/get_memorial", params={"project": "demo"})
    assert response.status_code == 200
    assert "Z_MEMORIAL.md non trouvé" in response.text


def test_get_memorial_serves_content(client, api_context):
    base_dir = api_context["base_dir"]
    memorial = base_dir / "projects" / "demo" / "fichiers" / "Z_MEMORIAL.md"
    memorial.parent.mkdir(parents=True, exist_ok=True)
    memorial.write_text("## Log\n- entry", encoding="utf-8")

    response = client.get("/get_memorial", params={"project": "demo"})
    assert response.status_code == 200
    assert response.text.strip().startswith("## Log")


def test_read_note_from_filepath(client, api_context):
    base_dir = api_context["base_dir"]
    note_path = base_dir / "projects" / "demo" / "fichiers" / "notes.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text("direct note content", encoding="utf-8")

    response = client.get("/read_note", params={"filepath": "projects/demo/fichiers/notes.md"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "direct note content" in data["results"][0]


def test_read_note_missing_filepath_returns_error(client):
    response = client.get(
        "/read_note",
        params={"filepath": "projects/demo/fichiers/missing.md"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "introuvable" in data["results"][0]


def test_read_note_uses_memory_search(client, api_context):
    client.post("/write_note", json={"text": "Planifier sprint demo", "project": "Demo"})

    response = client.get("/read_note", params={"term": "sprint"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert any("Planifier sprint demo" in line for line in data["results"])


def test_read_note_no_results(client):
    response = client.get("/read_note", params={"term": "absent"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "Aucune note" in data["results"][0]


def test_read_note_invalid_filepath(client):
    response = client.get("/read_note", params={"filepath": "  "})
    assert response.status_code == 400
