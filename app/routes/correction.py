from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
from pathlib import Path

from app.services.paths import get_base_dir

ALLOWED_BASE_DIR = get_base_dir().resolve()


router = APIRouter()


class CorrectionRequest(BaseModel):
    file_path: str
    agent_id: str


class CorrectionResponse(BaseModel):
    status: Literal["success", "error", "forbidden", "exception"]
    message: str | None = None
    output: str | None = None
    errors: str | None = None


@router.post(
    "/correct_file",
    response_model=CorrectionResponse,
    include_in_schema=False,
)
def correct_file_endpoint(request: CorrectionRequest):
    full_path = request.file_path

    if request.agent_id != "SENTRA_CORRECTOR++":
        return {"status": "forbidden", "message": "[error] Agent non autorise"}

    if not is_path_allowed(full_path):
        return {
            "status": "forbidden",
            "message": "[error] Ce fichier n'est pas dans la sandbox autorisee",
        }

    if not Path(full_path).exists():
        return {"status": "error", "message": f"[error] Fichier introuvable : {full_path}"}

    try:
        result = subprocess.run(
            ["python", "scripts/corrector/sentra_corrector_agent.py", full_path],
            capture_output=True,
            text=True,
            timeout=120,
        )

        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "errors": result.stderr.strip(),
        }

    except Exception as e:
        return {"status": "exception", "message": str(e)}



def is_path_allowed(path: str) -> bool:
    try:
        Path(path).resolve().relative_to(ALLOWED_BASE_DIR)
    except ValueError:
        return False
    return True
