from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.slow
def test_full_workflow_through_filesystem_and_memory(client, api_context):
    base_dir = api_context["base_dir"]

    note_text = "Organizer hands-off spec to CodeXpert"
    note_response = client.post(
        "/write_note",
        json={"text": note_text, "project": "demo"},
    )
    assert note_response.status_code == 200

    spec_body = "Initial spec drafted for CodeXpert"
    create_response = client.post(
        "/write_file",
        json={"project": "demo", "filename": "handoff/spec.md", "content": spec_body},
    )
    assert create_response.status_code == 200
    handoff_path = Path(create_response.json()["path"])
    assert handoff_path.exists()

    move_response = client.post(
        "/move_file",
        json={
            "src": "projects/demo/fichiers/handoff/spec.md",
            "dst": "projects/demo/fichiers/review/spec.md",
        },
    )
    assert move_response.status_code == 200
    assert move_response.json()["status"] == "success"

    archive_response = client.post(
        "/archive_file",
        json={
            "path": "projects/demo/fichiers/review/spec.md",
            "archive_dir": "archive/demo",
        },
    )
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "success"

    read_response = client.get("/read_note", params={"term": "hands-off"})
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["status"] == "success"
    combined = " ".join(data["results"]).lower()
    assert "organizer hands-off" in combined

    search_response = client.get(
        "/search",
        params={"term": "Initial spec", "dir": "archive/demo"},
    )
    assert search_response.status_code == 200
    archived_path = base_dir / "archive" / "demo" / "spec.md"
    assert str(archived_path) in search_response.json()["matches"]

    memorial_response = client.get("/get_memorial", params={"project": "demo"})
    assert memorial_response.status_code == 200
    assert "Organizer hands-off" in memorial_response.text

    commit_messages = [entry["message"] for entry in api_context["commits"]]
    assert any("GPT note" in message for message in commit_messages)
    assert any("GPT file update" in message for message in commit_messages)
    assert any("GPT move" in message for message in commit_messages)
    assert any("GPT archive" in message for message in commit_messages)
