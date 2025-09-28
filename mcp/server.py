from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mcp.middleware.ethics import log_charter_read
from mcp.middleware.rate_limit import RateLimitError, RateLimiter
from mcp.policies import fs_policy

API_BASE = (
    os.getenv("SENTRA_API_BASE")
    or os.getenv("API_BASE_URL")
    or "http://api:8000"
).rstrip("/")
RATE_LIMITER = RateLimiter(limit=5, window_seconds=10)

app = FastAPI(title="SENTRA MCP Sidecar", version="1.0.0")


class RAGDocumentPayload(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = Field(default=None, alias="doc_id")

    class Config:
        populate_by_name = True


class FilesReadArgs(BaseModel):
    user: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)


class FilesWriteArgs(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)
    content: str = Field(...)
    idempotency_key: Optional[str] = None


class N8NTriggerArgs(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: Optional[str] = None


class DocIndexArgs(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    documents: List[RAGDocumentPayload]


class DocQueryArgs(BaseModel):
    user: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    n_results: int = Field(5, ge=1, le=50)


class GitCommitArgs(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1)
    paths: List[str] = Field(..., min_items=1)
    message: str = Field(..., min_length=1)
    idempotency_key: Optional[str] = None


class SnapshotArgs(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    namespace: str = Field(..., min_length=1)
    summary_hint: Optional[str] = None


def _role_headers(role: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"X-ROLE": role}
    if extra:
        headers.update(extra)
    return headers


def _post(endpoint: str, payload: Dict[str, Any], role: str) -> Dict[str, Any]:
    url = f"{API_BASE}{endpoint}"
    try:
        response = requests.post(
            url, json=payload, headers=_role_headers(role), timeout=30
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Erreur réseau vers API: {exc}")
    # Si erreur côté API, renvoie le texte tel quel (souvent du JSON FastAPI)
    if response.status_code >= 400:
        detail = response.text
        # Essaie de rendre “json” si possible
        try:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        except ValueError:
            raise HTTPException(status_code=response.status_code, detail=detail)
    try:
        return response.json()
    except ValueError:
        return {"content": response.text, "status_code": response.status_code}


def _check_rate(tool: str, agent: Optional[str]) -> None:
    try:
        RATE_LIMITER.hit(tool, agent or "")
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))


@app.post("/tools/files.read")
def tool_files_read(args: FilesReadArgs) -> Dict[str, Any]:
    _check_rate("files.read", args.user)
    log_charter_read("files.read", args.user, None)
    path = fs_policy.ensure_library_path(args.path)
    return _post("/files/read", {"user": args.user, "path": str(path)}, role="reader")


@app.post("/tools/files.write")
def tool_files_write(args: FilesWriteArgs) -> Dict[str, Any]:
    _check_rate("files.write", args.agent)
    log_charter_read("files.write", args.user, args.agent)
    topic_hint = Path(args.path).stem or "note"
    target_path = fs_policy.ensure_library_path(args.path, args.agent, topic_hint)
    payload = {
        "user": args.user,
        "agent": args.agent,
        "path": str(target_path),
        "content": args.content,
        "idempotency_key": args.idempotency_key,
    }
    return _post("/files/write", payload, role="writer")


@app.post("/tools/n8n.trigger")
def tool_n8n_trigger(args: N8NTriggerArgs) -> Dict[str, Any]:
    _check_rate("n8n.trigger", args.agent)
    log_charter_read("n8n.trigger", args.user, args.agent)
    payload = {
        "user": args.user,
        "agent": args.agent,
        "payload": args.payload,
        "idempotency_key": args.idempotency_key,
    }
    return _post("/n8n/trigger", payload, role="writer")


@app.post("/tools/doc.index")
def tool_doc_index(args: DocIndexArgs) -> Dict[str, Any]:
    _check_rate("doc.index", args.agent)
    log_charter_read("doc.index", args.user, args.agent)
    documents: List[Dict[str, Any]] = []
    for doc in args.documents:
        if not doc.metadata.get("source"):
            raise HTTPException(status_code=400, detail="metadata.source obligatoire pour l’indexation")
        source_path = fs_policy.ensure_library_path(str(doc.metadata["source"]))
        metadata = fs_policy.ensure_metadata_source(doc.metadata, source_path)
        documents.append({
            "text": doc.text,
            "metadata": metadata,
            "id": doc.id,
        })
    payload = {
        "user": args.user,
        "agent": args.agent,
        "collection": args.collection,
        "documents": documents,
    }
    return _post("/rag/index", payload, role="writer")


@app.post("/tools/doc.query")
def tool_doc_query(args: DocQueryArgs) -> Dict[str, Any]:
    _check_rate("doc.query", args.user)
    log_charter_read("doc.query", args.user, None)
    payload = {
        "user": args.user,
        "collection": args.collection,
        "query": args.query,
        "n_results": args.n_results,
    }
    return _post("/rag/query", payload, role="reader")


@app.post("/tools/git.commit_push")
def tool_git_commit(args: GitCommitArgs) -> Dict[str, Any]:
    _check_rate("git.commit_push", args.agent)
    log_charter_read("git.commit_push", args.user, args.agent)
    payload = {
        "user": args.user,
        "agent": args.agent,
        "branch": args.branch,
        "paths": args.paths,
        "message": args.message,
        "idempotency_key": args.idempotency_key,
    }
    return _post("/git/commitPush", payload, role="writer")


@app.post("/tools/conversation.snapshot.save")
def tool_snapshot(args: SnapshotArgs) -> Dict[str, Any]:
    _check_rate("conversation.snapshot.save", args.agent)
    log_charter_read("conversation.snapshot.save", args.user, args.agent)
    topic = args.namespace
    filename = fs_policy.ensure_library_path(
        f"/memory/snapshots/{args.namespace}/{args.namespace}.md",
        agent=args.agent,
        topic=topic,
    )
    content_lines = [
        f"# Snapshot {args.namespace}",
        "", f"Agent : {args.agent}", f"Utilisateur : {args.user}",
    ]
    if args.summary_hint:
        content_lines.extend(["", f"Résumé : {args.summary_hint}"])
    payload = {
        "user": args.user,
        "agent": args.agent,
        "path": str(filename),
        "content": "\n".join(content_lines) + "\n",
    }
    result = _post("/files/write", payload, role="writer")
    return {"snapshot_path": result.get("path")}
