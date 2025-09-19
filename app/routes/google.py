from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

from app.dependencies import get_audit_logger, get_google_auth_manager
from app.services.audit import AuditLogger
from app.services.google_clients import GoogleAuthManager, GoogleCredentialsError

router = APIRouter(tags=["google"])


def _ensure_timezone(value: datetime, fallback: str | None) -> Dict[str, str]:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return {
        "dateTime": value.isoformat(),
        "timeZone": fallback or value.tzinfo.tzname(value) or "UTC",
    }


class GCalCreateEventRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    calendar_id: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    description: str | None = None
    location: str | None = None
    start: datetime
    end: datetime
    timezone: str | None = Field(default=None)
    attendees: List[str] = Field(default_factory=list)
    idempotency_key: str | None = None


class GCalCreateEventResponse(BaseModel):
    event_id: str
    html_link: str | None
    status: str


@router.post("/google/gcal/create_event", name="gcal.create_event")
def create_gcal_event(
    request: GCalCreateEventRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    auth_manager: GoogleAuthManager = Depends(get_google_auth_manager),
) -> GCalCreateEventResponse:
    audit_logger.log("gcal.create_event", request.model_dump(exclude={"user"}), request.user)
    try:
        service = auth_manager.calendar_service()
    except GoogleCredentialsError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    event_body: Dict[str, Any] = {
        "summary": request.summary,
        "description": request.description,
        "location": request.location,
        "start": _ensure_timezone(request.start, request.timezone),
        "end": _ensure_timezone(request.end, request.timezone),
        "attendees": [{"email": email} for email in request.attendees],
    }
    event_id = None
    if request.idempotency_key:
        event_id = request.idempotency_key.replace(" ", "-")
        event_body["id"] = event_id
    try:
        created = service.events().insert(
            calendarId=request.calendar_id,
            body=event_body,
            supportsAttachments=True,
            sendUpdates="all",
        ).execute()
    except HttpError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return GCalCreateEventResponse(
        event_id=created.get("id", event_id or ""),
        html_link=created.get("htmlLink"),
        status=created.get("status", "confirmed"),
    )


class GDriveUploadRequest(BaseModel):
    user: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    mime_type: str = Field(..., min_length=1)
    content_base64: str = Field(..., description="Base64-encoded file content")
    folder_id: str | None = Field(default=None)


class GDriveUploadResponse(BaseModel):
    file_id: str
    web_view_link: str | None


@router.post("/google/gdrive/upload", name="gdrive.upload")
def upload_to_gdrive(
    request: GDriveUploadRequest,
    audit_logger: AuditLogger = Depends(get_audit_logger),
    auth_manager: GoogleAuthManager = Depends(get_google_auth_manager),
) -> GDriveUploadResponse:
    audit_logger.log("gdrive.upload", request.model_dump(exclude={"user"}), request.user)
    try:
        service = auth_manager.drive_service()
    except GoogleCredentialsError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    try:
        binary_content = base64.b64decode(request.content_base64)
    except binascii.Error as error:
        raise HTTPException(status_code=400, detail="Invalid base64 content") from error
    metadata: Dict[str, Any] = {"name": request.name}
    if request.folder_id:
        metadata["parents"] = [request.folder_id]
    media = auth_manager.build_media(binary_content, request.mime_type)
    try:
        created = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink",
        ).execute()
    except HttpError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return GDriveUploadResponse(
        file_id=created.get("id", ""),
        web_view_link=created.get("webViewLink"),
    )
