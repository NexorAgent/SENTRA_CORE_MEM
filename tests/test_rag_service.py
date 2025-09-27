from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_audit_logger, get_rag_service
from app.main import create_app
from app.services.rag_service import RAGDocument, RAGService


class _DummyAuditLogger:
    def log(self, *args, **kwargs) -> None:  # pragma: no cover - logging no-op
        return None


@pytest.fixture()
def rag_service(tmp_path) -> Iterator[RAGService]:
    service = RAGService(persist_directory=tmp_path / "chroma")
    yield service


@pytest.fixture()
def rag_client(tmp_path) -> Iterator[TestClient]:
    app = create_app()
    service = RAGService(persist_directory=tmp_path / "chroma_api")

    app.dependency_overrides[get_rag_service] = lambda: service
    app.dependency_overrides[get_audit_logger] = lambda: _DummyAuditLogger()

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


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
    rag_service.index("unit", documents)

    matches = rag_service.query("unit", "alpha", n_results=2)

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
