from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_git_helper
from app.services.audit import AuditLogger
from app.services.git_ops import GitOpsError, GitOpsHelper
from app.services.paths import resolve_workspace_path

router = APIRouter(tags=["git"])


class GitCommitRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1)
    paths: List[str] = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    idempotency_key: str | None = None


class GitCommitResponse(BaseModel):
    branch: str
    committed: bool
    sha: str | None


@router.post("/git/commitPush", name="git.commitPush", operation_id="git.commitPush")
def commit_push(
    request: GitCommitRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    git_helper: GitOpsHelper = Depends(get_git_helper),
) -> GitCommitResponse:
    audit_logger.log("git.commitPush", request.model_dump(exclude={"user"}), request.user)
    if not request.paths:
        raise HTTPException(status_code=400, detail="paths ne peut pas être vide")
    try:
        resolved_paths = [resolve_workspace_path(path) for path in request.paths]
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    try:
        result = git_helper.commit_paths(
            branch=request.branch,
            paths=resolved_paths,
            message=request.message,
            agent=request.agent,
            idempotency_key=request.idempotency_key,
        )
    except GitOpsError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return GitCommitResponse(
        branch=request.branch,
        committed=bool(result.get("committed")),
        sha=result.get("sha"),
    )
