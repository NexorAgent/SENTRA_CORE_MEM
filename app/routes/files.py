from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_git_helper
from app.services.audit import AuditLogger
from app.services.git_ops import GitOpsError, GitOpsHelper
from app.services.paths import resolve_workspace_path

router = APIRouter(tags=["files"])


class FileReadRequest(BaseModel):
    path: str = Field(..., description="Path beginning with /projects, /reports, or /students")
    user: str = Field(..., min_length=1)


class FileReadResponse(BaseModel):
    path: str
    content: str
    sha256: str
    last_modified: datetime | None


class FileWriteRequest(FileReadRequest):
    content: str = Field(..., description="File contents to persist")
    agent: str = Field(..., min_length=1)
    idempotency_key: str | None = Field(None, description="Caller-supplied idempotency key")


class FileWriteResponse(BaseModel):
    path: str
    sha256: str
    committed: bool
    commit_message: str | None


@router.post("/files/read", name="files.read")
def read_file(request: FileReadRequest, audit_logger: AuditLogger = Depends(get_audit_logger)) -> FileReadResponse:
    audit_logger.log("files.read", request.model_dump(exclude={"user"}), request.user)
    try:
        target_path = resolve_workspace_path(request.path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    content = target_path.read_text(encoding="utf-8")
    digest = sha256(content.encode("utf-8")).hexdigest()
    stat = target_path.stat()
    last_modified = datetime.fromtimestamp(stat.st_mtime)
    return FileReadResponse(
        path=str(target_path),
        content=content,
        sha256=digest,
        last_modified=last_modified,
    )


@router.post("/files/write", name="files.write")
def write_file(
    request: FileWriteRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    git_helper: GitOpsHelper = Depends(get_git_helper),
) -> FileWriteResponse:
    audit_logger.log("files.write", request.model_dump(exclude={"user"}), request.user)
    try:
        target_path = resolve_workspace_path(request.path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    target_path.parent.mkdir(parents=True, exist_ok=True)
    existing_content = target_path.read_text(encoding="utf-8") if target_path.exists() else None
    if existing_content == request.content:
        digest = sha256(request.content.encode("utf-8")).hexdigest()
        return FileWriteResponse(
            path=str(target_path),
            sha256=digest,
            committed=False,
            commit_message=None,
        )
    target_path.write_text(request.content, encoding="utf-8")
    digest = sha256(request.content.encode("utf-8")).hexdigest()
    try:
        commit_message = git_helper.commit_and_push("files.write", target_path, request.agent, digest)
    except GitOpsError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return FileWriteResponse(
        path=str(target_path),
        sha256=digest,
        committed=commit_message is not None,
        commit_message=commit_message,
    )
