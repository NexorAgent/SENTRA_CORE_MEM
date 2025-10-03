from __future__ import annotations

import gzip
import json

from sqlalchemy import select

from app.db import session as session_module
from app.db.models.memory import MemoryNote as MemoryNoteModel


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

    archive_path = api_context["base_dir"] / "memory" / "library" / "archives" / f"{note['note_id']}.zmem"
    assert archive_path.exists()
    with gzip.open(archive_path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["text"] == "Capture meeting notes"

    with session_module.get_session() as session:
        stored = session.get(MemoryNoteModel, note["note_id"])
        assert stored is not None
        assert stored.text == "Capture meeting notes"

    assert any(event["tool"] == "memory.note.add" for event in api_context["audit_events"])


def test_memory_note_add_is_idempotent_with_same_note_id(client, api_context):
    first = _add_note(client, "Initial capture", note_id="note-1")
    second = _add_note(client, "Modified capture", note_id="note-1")

    assert first["created"] is True
    assert second["created"] is False

    with session_module.get_session() as session:
        notes = session.scalars(select(MemoryNoteModel)).all()
        assert len(notes) == 1
        assert notes[0].text == "Initial capture"

    archive_path = api_context["base_dir"] / "memory" / "library" / "archives" / f"{first['note']['note_id']}.zmem"
    with gzip.open(archive_path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["text"] == "Initial capture"


def test_memory_note_find_filters_by_query_and_tags(client, api_context):
    _add_note(client, "Planifier sprint demo", tags=["planning", "demo"])
    _add_note(client, "Reunion support", tags=["support"])

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
