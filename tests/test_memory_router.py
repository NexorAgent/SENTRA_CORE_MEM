from __future__ import annotations

import json


def _add_note(client, text: str, note_id: str | None = None, tags: list[str] | None = None) -> dict:
    payload = {
        "user": "operator",
        "agent": "scribe",
        "note": {
            "text": text,
            "tags": tags or [],
            "metadata": {"source": "tests"},
        },
    }
    if note_id:
        payload["note"]["note_id"] = note_id
    response = client.post("/memory/note/add", json=payload)
    assert response.status_code == 200
    return response.json()


def test_memory_note_add_persists_payload_and_logs(client, api_context):
    result = _add_note(client, "Capture meeting notes", tags=["meeting"])
    assert result["created"] is True
    note = result["note"]
    assert note["text"] == "Capture meeting notes"
    assert note["tags"] == ["meeting"]

    mem_file = api_context["base_dir"] / "memory" / "sentra_memory.json"
    assert mem_file.exists()
    saved = json.loads(mem_file.read_text(encoding="utf-8"))
    assert saved[0]["text"] == "Capture meeting notes"

    assert any(event["tool"] == "memory.note.add" for event in api_context["audit_events"])


def test_memory_note_add_is_idempotent_with_same_note_id(client, api_context):
    first = _add_note(client, "Initial capture", note_id="note-1")
    second = _add_note(client, "Modified capture", note_id="note-1")

    assert first["created"] is True
    assert second["created"] is False

    mem_file = api_context["base_dir"] / "memory" / "sentra_memory.json"
    entries = json.loads(mem_file.read_text(encoding="utf-8"))
    assert len(entries) == 1
    assert entries[0]["text"] == "Initial capture"


def test_memory_note_find_filters_by_query_and_tags(client, api_context):
    _add_note(client, "Planifier sprint demo", tags=["planning", "demo"])
    _add_note(client, "Réunion support", tags=["support"])

    response = client.post(
        "/memory/note/find",
        json={
            "user": "operator",
            "query": "sprint",
            "tags": ["planning"],
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["text"] == "Planifier sprint demo"
    assert any(event["tool"] == "memory.note.find" for event in api_context["audit_events"])


def test_memory_note_find_returns_empty_when_no_matches(client):
    response = client.post(
        "/memory/note/find",
        json={"user": "operator", "query": "absent", "tags": [], "limit": 3},
    )
    assert response.status_code == 200
    assert response.json()["results"] == []
