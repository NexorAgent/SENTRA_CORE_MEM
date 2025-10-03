from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app import dependencies as dependencies_module
from app.db import session as session_module
from app.main import create_app
from app.services.rag_service import RAGDocument, RAGService


class _DummyAuditLogger:
    def log(self, *args, **kwargs) -> None:  # pragma: no cover - logging no-op
        return None


@pytest.fixture()
def rag_service(api_context) -> RAGService:
    dependencies_module.get_rag_service.cache_clear()
    return RAGService()


@pytest.fixture()
def rag_client(client) -> Iterator[TestClient]:
    dependencies_module.get_rag_service.cache_clear()
    client.app.dependency_overrides[dependencies_module.get_rag_service] = dependencies_module.get_rag_service
    client.app.dependency_overrides[dependencies_module.get_audit_logger] = lambda: _DummyAuditLogger()
    yield client


def test_rag_service_returns_structured_matches(rag_service: RAGService) -> None:
    documents = [
        RAGDocument(
            doc_id="doc-1",
            text="Alpha beta gamma",
            metadata={"source": "notes/doc-1.md"},
        ),
        RAGDocument(
            doc_id="doc-2",
            text="Delta epsilon zeta",
            metadata={"source": "notes/doc-2.md"},
        ),
    ]
    with session_module.get_session() as session:
        rag_service.index(session, "unit", documents)
        matches = rag_service.query(session, "unit", "alpha", n_results=2)

    assert isinstance(matches, list)
    assert matches
    assert all("excerpt" in match for match in matches)
    assert all("source" in match for match in matches)
    assert all("score" in match for match in matches)

    alpha_match = next((match for match in matches if match["source"] == "notes/doc-1.md"), None)
    assert alpha_match is not None
    assert alpha_match["excerpt"] == "Alpha beta gamma"
    assert isinstance(alpha_match["score"], float)


def test_rag_query_endpoint_includes_source_metadata(rag_client: TestClient) -> None:
    index_payload = {
        "user": "tester",
        "agent": "unit",
        "collection": "integration",
        "documents": [
            {
                "text": "Wizardry of the ancient code",
                "metadata": {"source": "projects/demo/wizards.md"},
            },
            {
                "text": "The chronicles of diligent testing",
                "metadata": {"source": "projects/demo/testing.md"},
            },
        ],
    }
    index_response = rag_client.post("/rag/index", json=index_payload)
    assert index_response.status_code == 200

    query_payload = {
        "user": "tester",
        "collection": "integration",
        "query": "wizardry",
        "n_results": 2,
    }
    query_response = rag_client.post("/rag/query", json=query_payload)
    assert query_response.status_code == 200

    body = query_response.json()
    assert isinstance(body["results"], list)
    assert body["results"]
    assert all(hit["source"] for hit in body["results"])
    assert all(isinstance(hit["score"], float) for hit in body["results"])

    wizard_hit = next((hit for hit in body["results"] if hit["source"] == "projects/demo/wizards.md"), None)
    assert wizard_hit is not None
    assert wizard_hit["excerpt"] == "Wizardry of the ancient code"
