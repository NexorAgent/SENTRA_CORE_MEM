from __future__ import annotations

from fastapi import FastAPI

from app.routes.bus import router as bus_router
from app.routes.correction import router as correction_router
from app.routes.files import router as files_router
from app.routes.git import router as git_router
from app.routes.google import router as google_router
from app.routes.memory import router as memory_router
from app.routes.n8n import router as n8n_router
from app.routes.rag import router as rag_router
from app.routes.zep import router as zep_router


def create_app() -> FastAPI:
    app = FastAPI(title="SENTRA API", version="1.0.0")

    @app.get("/", include_in_schema=False)
    def health_check() -> dict[str, str]:
        return {"status": "ok", "message": "SENTRA API active"}

    app.include_router(files_router)
    app.include_router(memory_router)
    app.include_router(n8n_router)
    app.include_router(google_router)
    app.include_router(bus_router)
    app.include_router(rag_router)
    app.include_router(correction_router)
    app.include_router(git_router)
    app.include_router(zep_router)

    return app


app = create_app()
