from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from scripts.memory_zep_local import save_to_zep, search_zep

router = APIRouter(prefix="/zep", tags=["zep"], include_in_schema=False)


class ZepPayload(BaseModel):
    session_id: str
    role: str
    content: str


@router.post("/save")
def zep_save(payload: ZepPayload) -> dict:
    try:
        response = save_to_zep(payload.session_id, payload.role, payload.content)
        return {"status": "ok", "zep_response": response.json()}
    except Exception as error:  # pragma: no cover - upstream dependency
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/search")
def zep_search(session_id: str = Query(...), query: str = Query(...)) -> dict:
    try:
        results = search_zep(session_id, query)
        return {"status": "ok", "results": results}
    except Exception as error:  # pragma: no cover - upstream dependency
        raise HTTPException(status_code=500, detail=str(error)) from error
