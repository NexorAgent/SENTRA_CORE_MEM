# app/middleware/route_guard.py
from __future__ import annotations

from typing import Iterable, Callable, Set

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # stocke le rôle dans request.state.role (si header absent -> "unknown")
        role = request.headers.get("X-ROLE") or request.headers.get("x-role")
        request.state.role = role or "unknown"
        return await call_next(request)


def rbac_guard(app) -> None:
    """
    Raccourci pour ajouter la middleware RBAC globale.
    """
    app.add_middleware(RBACMiddleware)


def require_role(allowed: Iterable[str]) -> Callable:
    """
    Dépendance FastAPI : bloque si le rôle courant n'est pas dans `allowed`.
    Utilisée pour certaines routes (ex: Google).
    """
    allowed_set: Set[str] = set(allowed)

    async def _dep(request: Request) -> None:
        role = (
            request.headers.get("X-ROLE")
            or request.headers.get("x-role")
            or getattr(request.state, "role", None)
        )
        if not role or role not in allowed_set:
            raise HTTPException(status_code=403, detail="RBAC: role not allowed")

    return _dep
