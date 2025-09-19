from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_n8n_client
from app.services.audit import AuditLogger
from app.services.n8n_client import N8NClient, N8NConfigurationError

router = APIRouter(tags=["n8n"])


class N8NTriggerRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None)


class N8NTriggerResponse(BaseModel):
    result: Dict[str, Any]


@router.post("/n8n/trigger", name="n8n.trigger")
def trigger_workflow(
    request: N8NTriggerRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client: N8NClient = Depends(get_n8n_client),
) -> N8NTriggerResponse:
    audit_logger.log("n8n.trigger", request.model_dump(exclude={"user"}), request.user)
    try:
        result = client.trigger(request.payload, idempotency_key=request.idempotency_key or request.agent)
    except N8NConfigurationError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except Exception as error:  # pragma: no cover - requests errors propagate
        raise HTTPException(status_code=502, detail=str(error)) from error
    return N8NTriggerResponse(result=result)
