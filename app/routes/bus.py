from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_bus_service
from app.services.audit import AuditLogger
from app.services.bus_service import BusService, BusServiceError

router = APIRouter(tags=["bus"])


class BusSendRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    spreadsheet_id: str = Field(..., min_length=1)
    worksheet: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class BusSendResponse(BaseModel):
    message_id: str
    status: str
    timestamp: str


class BusPollRequest(BaseModel):
    user: str = Field(..., min_length=1)
    spreadsheet_id: str = Field(..., min_length=1)
    worksheet: str = Field(..., min_length=1)
    status: str | None = None
    limit: int = Field(20, ge=1, le=100)


class BusRecord(BaseModel):
    message_id: str
    timestamp: str
    user: str
    agent: str
    status: str
    payload: Dict[str, Any]


class BusPollResponse(BaseModel):
    records: List[BusRecord]


class BusUpdateStatusRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    spreadsheet_id: str = Field(..., min_length=1)
    worksheet: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    error: str | None = None


class BusUpdateStatusResponse(BaseModel):
    message_id: str
    status: str
    timestamp: str


@router.post("/bus/send", name="bus.send", operation_id="bus.send")
def bus_send(
    request: BusSendRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: BusService = Depends(get_bus_service),
) -> BusSendResponse:
    audit_logger.log("bus.send", request.model_dump(exclude={"user"}), request.user)
    try:
        result = service.send(
            spreadsheet_id=request.spreadsheet_id,
            worksheet=request.worksheet,
            payload=request.payload,
            user=request.user,
            agent=request.agent,
            idempotency_key=request.idempotency_key,
        )
    except BusServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return BusSendResponse(**result)


@router.post("/bus/poll", name="bus.poll", operation_id="bus.poll")
def bus_poll(
    request: BusPollRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: BusService = Depends(get_bus_service),
) -> BusPollResponse:
    audit_logger.log("bus.poll", request.model_dump(exclude={"user"}), request.user)
    try:
        records = service.poll(
            spreadsheet_id=request.spreadsheet_id,
            worksheet=request.worksheet,
            status=request.status,
            limit=request.limit,
        )
    except BusServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return BusPollResponse(records=[BusRecord(**record) for record in records])


@router.post(
    "/bus/updateStatus",
    name="bus.updateStatus",
    operation_id="bus.updateStatus",
)
def bus_update_status(
    request: BusUpdateStatusRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    service: BusService = Depends(get_bus_service),
) -> BusUpdateStatusResponse:
    audit_logger.log("bus.updateStatus", request.model_dump(exclude={"user"}), request.user)
    try:
        result = service.update_status(
            spreadsheet_id=request.spreadsheet_id,
            worksheet=request.worksheet,
            message_id=request.message_id,
            status=request.status,
            error=request.error,
            agent=request.agent,
        )
    except BusServiceError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return BusUpdateStatusResponse(**result)
