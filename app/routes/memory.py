from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dependencies import (
    get_audit_logger,
    get_db_session,
    get_memory_service,
)
from app.memory.domain import MemoryNoteDTO
from app.memory.service import MemoryService
from app.services.audit import AuditLogger

router = APIRouter(tags=["memory"])


class MemoryNotePayload(BaseModel):
    text: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    note_id: str | None = Field(default=None, description="Explicit note identifier to enforce idempotency")


class MemoryNoteAddRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    note: MemoryNotePayload


class MemoryNoteModel(BaseModel):
    note_id: str
    user: str
    agent: str
    text: str
    tags: List[str]
    metadata: Dict[str, Any]
    score: float | None = None
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, note: MemoryNoteDTO) -> "MemoryNoteModel":
        return cls(
            note_id=note.note_id,
            user=note.user,
            agent=note.agent,
            text=note.text,
            tags=note.tags,
            metadata=note.metadata,
            score=note.score,
            created_at=note.created_at.isoformat(),
            updated_at=note.updated_at.isoformat(),
        )


class MemoryNoteAddResponse(BaseModel):
    note: MemoryNoteModel
    created: bool


class MemoryNoteFindRequest(BaseModel):
    user: str = Field(..., min_length=1)
    query: str = Field("", description="Full-text query string")
    tags: List[str] = Field(default_factory=list)
    limit: int = Field(20, ge=1, le=100)


class MemoryNoteFindResponse(BaseModel):
    results: List[MemoryNoteModel]


@router.post(
    "/memory/note/add",
    name="memory.note.add",
    operation_id="memory.note.add",
)
def add_memory_note(
    request: MemoryNoteAddRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: MemoryService = Depends(get_memory_service),
    session: Session = Depends(get_db_session),
) -> MemoryNoteAddResponse:
    audit_logger.log("memory.note.add", request.model_dump(exclude={"user"}), request.user)
    note, created = service.add_note(
        session,
        user=request.user,
        agent=request.agent,
        text=request.note.text,
        tags=request.note.tags,
        metadata=request.note.metadata,
        note_id=request.note.note_id,
    )
    return MemoryNoteAddResponse(note=MemoryNoteModel.from_domain(note), created=created)


@router.post(
    "/memory/note/find",
    name="memory.note.find",
    operation_id="memory.note.find",
)
def find_memory_notes(
    request: MemoryNoteFindRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: MemoryService = Depends(get_memory_service),
    session: Session = Depends(get_db_session),
) -> MemoryNoteFindResponse:
    audit_logger.log("memory.note.find", request.model_dump(exclude={"user"}), request.user)
    notes = service.find_notes(
        session,
        query=request.query,
        tags=request.tags,
        limit=request.limit,
    )
    return MemoryNoteFindResponse(results=[MemoryNoteModel.from_domain(note) for note in notes])
