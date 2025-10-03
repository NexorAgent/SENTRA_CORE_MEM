from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import get_audit_logger, get_db_session, get_rag_service
from app.services.audit import AuditLogger
from app.services.rag_service import RAGDocument, RAGService

router = APIRouter(tags=["rag"])


class RAGDocumentPayload(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_id: str | None = Field(default=None, alias="id")

    def compute_id(self) -> str:
        if self.document_id:
            return self.document_id
        fingerprint = json.dumps(
            {"text": self.text, "metadata": self.metadata},
            sort_keys=True,
            ensure_ascii=False,
        )
        return sha256(fingerprint.encode("utf-8")).hexdigest()


class RAGIndexRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    documents: List[RAGDocumentPayload]


class RAGIndexResponse(BaseModel):
    document_ids: List[str]


class RAGQueryRequest(BaseModel):
    user: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    n_results: int = Field(5, ge=1, le=50)


class RAGQueryHit(BaseModel):
    excerpt: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    score: float
    metadata: Dict[str, Any] | None = None


class RAGQueryResponse(BaseModel):
    results: List[RAGQueryHit] = Field(default_factory=list)


@router.post("/rag/index", name="rag.index", operation_id="rag.index")
def rag_index(
    request: RAGIndexRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: RAGService = Depends(get_rag_service),
    session: Session = Depends(get_db_session),
) -> RAGIndexResponse:
    audit_logger.log("rag.index", request.model_dump(exclude={"user"}), request.user)
    if not request.documents:
        raise HTTPException(status_code=400, detail="At least one document is required")
    documents = [
        RAGDocument(doc_id=doc.compute_id(), text=doc.text, metadata=doc.metadata)
        for doc in request.documents
    ]
    try:
        ids = service.index(session, request.collection, documents)
    except Exception as error:  # pragma: no cover - runtime errors propagate
        raise HTTPException(status_code=500, detail=str(error)) from error
    return RAGIndexResponse(document_ids=ids)


@router.post("/rag/query", name="rag.query", operation_id="rag.query")
def rag_query(
    request: RAGQueryRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: RAGService = Depends(get_rag_service),
    session: Session = Depends(get_db_session),
) -> RAGQueryResponse:
    audit_logger.log("rag.query", request.model_dump(exclude={"user"}), request.user)
    try:
        result = service.query(session, request.collection, request.query, request.n_results)
    except Exception as error:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(error)) from error
    return RAGQueryResponse(results=result)

