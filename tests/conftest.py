import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.routes.correction as correction
import scripts.api_sentra as api


@pytest.fixture
def api_context(tmp_path, monkeypatch):
    base_dir = tmp_path / "sentra"
    for sub in ("projects", "memory", "logs", "archive"):
        (base_dir / sub).mkdir(parents=True, exist_ok=True)

    commits: list[dict[str, object]] = []

    def fake_git_commit_push(paths, message):
        normalized = [Path(p) for p in paths]
        commits.append({"paths": normalized, "message": message})

    monkeypatch.setattr(api, "git_commit_push", fake_git_commit_push)

    def fake_search_memory(term: str, max_results: int = 5):
        mem_file = base_dir / "memory" / "sentra_memory.json"
        if not mem_file.exists():
            return []
        data = json.loads(mem_file.read_text(encoding="utf-8"))
        results: list[str] = []
        for entry in data:
            if term.lower() in entry.get("text", "").lower():
                ts = entry.get("timestamp", "now")
                results.append(f"- [{ts}] {entry['text']}")
            if len(results) >= max_results:
                break
        return results

    monkeypatch.setattr(api, "search_memory", fake_search_memory)

    def fake_query_memory(limit: int):
        mem_file = base_dir / "memory" / "sentra_memory.json"
        if not mem_file.exists():
            return []
        data = json.loads(mem_file.read_text(encoding="utf-8"))
        return data[-limit:]

    monkeypatch.setattr(api, "query_memory", fake_query_memory)

    monkeypatch.setattr(api, "BASE_DIR", base_dir)

    sandbox_root = (base_dir / "sandbox" / "SENTRA_SANDBOX").resolve()
    sandbox_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(correction, "ALLOWED_BASE_DIR", str(sandbox_root))

    return {"base_dir": base_dir, "commits": commits, "sandbox": sandbox_root}


@pytest.fixture
def client(api_context):
    with TestClient(api.app) as test_client:
        yield test_client
