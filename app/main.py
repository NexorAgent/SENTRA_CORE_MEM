from fastapi import FastAPI, HTTPException, Query
from app.routes.correction import router as correction_router
from scripts.memory_zep_local import save_to_zep, search_zep
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "SENTRA API active"}

# Route correction
app.include_router(correction_router)

# === ROUTES ZEP ===

class ZepPayload(BaseModel):
    session_id: str
    role: str
    content: str

@app.post("/zep/save")
def api_zep_save(payload: ZepPayload):
    try:
        res = save_to_zep(payload.session_id, payload.role, payload.content)
        return {"status": "ok", "zep_response": res.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/zep/search")
def api_zep_search(session_id: str = Query(...), query: str = Query(...)):
    try:
        results = search_zep(session_id, query)
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
