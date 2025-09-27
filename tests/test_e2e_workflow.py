from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.slow
def test_full_workflow_using_mcp_endpoints(client, api_context):
    note_text = "Organizer hands-off spec to CodeXpert"
    note_response = client.post(
        "/memory/note/add",
        json={
            "user": "operator",
            "agent": "scribe",
            "note": {
                "text": note_text,
                "tags": ["handoff", "spec"],
                "metadata": {"channel": "ops"},
            },
        },
    )
    assert note_response.status_code == 200
    note_payload = note_response.json()["note"]
    assert note_payload["text"] == note_text

    spec_content = "Initial spec drafted for CodeXpert"
    write_response = client.post(
        "/files/write",
        json={
            "user": "operator",
            "agent": "scribe",
            "path": "/projects/demo/docs/spec.md",
            "content": spec_content,
        },
    )
    assert write_response.status_code == 200
    written_path = write_response.json()["path"]

    read_response = client.post(
        "/files/read",
        json={"user": "operator", "path": "/projects/demo/docs/spec.md"},
    )
    assert read_response.status_code == 200
    assert spec_content in read_response.json()["content"]

    find_response = client.post(
        "/memory/note/find",
        json={"user": "operator", "query": "CodeXpert", "tags": [], "limit": 5},
    )
    assert find_response.status_code == 200
    matches = [entry["text"] for entry in find_response.json()["results"]]
    assert any(note_text in item for item in matches)

    commits = [entry["message"] for entry in api_context["git_commits"]]
    assert any("files.write" in message for message in commits)
    assert any(event["tool"] == "memory.note.add" for event in api_context["audit_events"])

    persisted = api_context["base_dir"] / "projects" / "demo" / "docs" / "spec.md"
    assert persisted.exists() and persisted.read_text(encoding="utf-8") == spec_content
    assert written_path == str(persisted)


def test_bus_flow_covering_send_poll_and_update(client, api_context):
    send_response = client.post(
        "/bus/send",
        json={
            "user": "operator",
            "agent": "dispatcher",
            "payload": {"title": "Onboarding"},
            "metadata": {"spreadsheet_id": "sheet-1", "worksheet": "Requests"},
        },
    )
    assert send_response.status_code == 200
    send_payload = send_response.json()
    message_id = send_payload["message_id"]
    assert send_payload["status"] == "pending"

    update_response = client.post(
        "/bus/updateStatus",
        json={
            "user": "operator",
            "agent": "dispatcher",
            "message_id": message_id,
            "status": "done",
            "metadata": {"spreadsheet_id": "sheet-1", "worksheet": "Requests"},
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "done"

    poll_response = client.post(
        "/bus/poll",
        json={
            "user": "operator",
            "agent": "dispatcher",
            "status": "done",
            "limit": 5,
            "metadata": {"spreadsheet_id": "sheet-1", "worksheet": "Requests"},
        },
    )
    assert poll_response.status_code == 200
    records = poll_response.json()["records"]
    assert len(records) == 1
    assert records[0]["message_id"] == message_id
    assert records[0]["status"] == "done"

    assert any(event["tool"].startswith("bus.") for event in api_context["audit_events"])


def test_google_flow_for_calendar_and_drive(client, api_context):
    start = datetime.now(timezone.utc).replace(microsecond=0)
    end = start + timedelta(hours=1)

    calendar_response = client.post(
        "/google/gcal/create_event",
        json={
            "user": "operator",
            "agent": "scheduler",
            "calendar_id": "primary",
            "summary": "Project Sync",
            "description": "Discuss launch",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "timezone": "UTC",
            "attendees": ["lead@example.com"],
            "idempotency_key": "sync-1",
        },
    )
    assert calendar_response.status_code == 200
    event_payload = calendar_response.json()
    assert event_payload["event_id"] == "sync-1"
    assert event_payload["status"] == "confirmed"

    encoded = base64.b64encode(b"Spec summary").decode("ascii")
    drive_response = client.post(
        "/google/gdrive/upload",
        json={
            "user": "operator",
            "agent": "scheduler",
            "name": "summary.txt",
            "mime_type": "text/plain",
            "content_base64": encoded,
            "folder_id": "folder-1",
        },
    )
    assert drive_response.status_code == 200
    file_payload = drive_response.json()
    assert file_payload["file_id"].startswith("file-")

    calendar_records = api_context["google_manager"].calendar.created_events
    assert any(entry["body"]["summary"] == "Project Sync" for entry in calendar_records)
    drive_records = api_context["google_manager"].drive.uploads
    assert any(upload["body"]["name"] == "summary.txt" for upload in drive_records)


def test_rag_index_and_query_flow(client, api_context):
    index_response = client.post(
        "/rag/index",
        json={
            "user": "operator",
            "agent": "researcher",
            "collection": "handbook",
            "documents": [
                {"text": "SENTRA handbook overview", "metadata": {"section": "intro", "source": "handbook/intro.md"}},
                {
                    "text": "Troubleshooting CodeXpert workflows",
                    "metadata": {"section": "support", "source": "handbook/support.md"},
                },
            ],
        },
    )
    assert index_response.status_code == 200
    indexed_ids = index_response.json()["document_ids"]
    assert len(indexed_ids) == 2

    query_response = client.post(
        "/rag/query",
        json={
            "user": "operator",
            "collection": "handbook",
            "query": "CodeXpert",
            "n_results": 3,
        },
    )
    assert query_response.status_code == 200
    rag_results = query_response.json()["results"]
    assert rag_results
    assert any("CodeXpert" in hit["excerpt"] for hit in rag_results)
    rag_collection = api_context["rag_service"].collections["handbook"]
    assert set(rag_collection) == set(indexed_ids)
