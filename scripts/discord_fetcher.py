import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime

# --------------------------------------
# Serve plugin manifest and static files
# --------------------------------------
app = FastAPI(
    title="Sentra Memory Plugin API",
    version="1.1.0",
    description="API pour piloter la reprise et l'écriture dans un projet SENTRA (Discord ↔ résumé GPT, notes, fichiers)."
)

@app.get("/ai-plugin.json", include_in_schema=False)
async def get_ai_plugin():
    # Sert le fichier ai-plugin.json depuis la racine
    path = Path(__file__).resolve().parent.parent / "ai-plugin.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="ai-plugin.json not found")
    return FileResponse(path, media_type="application/json")

@app.get("/logo.png", include_in_schema=False)
async def get_logo():
    # Sert un logo par défaut ou un fichier existant
    path = Path(__file__).resolve().parent.parent / "logo.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="logo.png not found")
    return FileResponse(path, media_type="image/png")

# -------------------------------
#  Modèles de requête / réponse
# -------------------------------
class RepriseRequest(BaseModel):
    project: str

class RepriseResponse(BaseModel):
    status: str
    resume_path: str | None = None
    resume_content: str | None = None
    detail: str | None = None

class WriteNoteRequest(BaseModel):
    text: str  # contenu de la note à enregistrer
    project: str | None = None

class WriteFileRequest(BaseModel):
    project: str        # e.g. "SENTRA_CORE"
    filename: str       # ex. "nouveau_guide.md"
    content: str        # contenu brut (Markdown/texte) à écrire

class WriteResponse(BaseModel):
    status: str
    detail: str | None = None
    path: str | None = None

# -------------------------------
#  Route 1: reprise de projet
# -------------------------------
@app.post("/reprise", response_model=RepriseResponse)
async def reprise_projet(req: RepriseRequest):
    projet = req.project.strip()

    # 1) Discord Fetcher
    cmd1 = f"python scripts/discord_fetcher.py {projet}"
    # 2) Project Resume (brut)
    cmd2 = f"python scripts/project_resume.py {projet}"
    # 3) Projet Resumer GPT (final)
    cmd3 = f"python scripts/project_resumer_gpt.py {projet}"

    for cmd in (cmd1, cmd2, cmd3):
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            return RepriseResponse(
                status="error",
                detail=f"Échec de `{cmd}` : {process.stderr}"
            )

    # Repérer le dernier résumé GPT
    project_slug = projet.lower().replace(" ", "_")
    resume_folder = Path("projects") / project_slug / "resume"
    if not resume_folder.exists():
        return RepriseResponse(
            status="error",
            detail=f"Aucun dossier resume pour {projet}."
        )
    resume_files = sorted(
        resume_folder.glob("resume_gpt2_*.md"),
        key=lambda f: f.stat().st_mtime
    )
    if not resume_files:
        return RepriseResponse(
            status="error",
            detail="Aucun résumé GPT final trouvé."
        )
    last = resume_files[-1]
    try:
        content = last.read_text(encoding="utf-8")
    except Exception as e:
        return RepriseResponse(
            status="error",
            detail=f"Impossible de lire {last}: {e}"
        )
    return RepriseResponse(
        status="success",
        resume_path=str(last),
        resume_content=content
    )

# ----------------------------------
#  Route 2: écriture d’une note simple
# ----------------------------------
@app.post("/write_note", response_model=WriteResponse)
async def write_note(req: WriteNoteRequest):
    """
    Enregistre une note dans la mémoire JSON (memory/sentra_memory.json).
    """
    from scripts.memory_agent import save_note_from_text
    from scripts.git_utils import git_commit_push

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    try:
        save_note_from_text(text)
    except Exception as e:
        return WriteResponse(status="error", detail=f"Erreur write_note: {e}")

    project_slug = req.project.strip().lower().replace(" ", "_") if req.project else "sentra_core"
    base_dir = Path("projects") / project_slug / "fichiers"
    base_dir.mkdir(parents=True, exist_ok=True)
    memoire_file = base_dir / f"memoire_{project_slug}.md"
    timestamp_md = datetime.now().strftime("## %Y-%m-%d %H:%M:%S\n- ")
    try:
        with memoire_file.open("a", encoding="utf-8") as mf:
            mf.write(f"{timestamp_md}{text}\n\n")
    except Exception as e:
        return WriteResponse(status="error", detail=f"Erreur écriture mémoire : {e}")

    mem_json = Path("memory") / "sentra_memory.json"
    try:
        git_commit_push([mem_json, memoire_file], f"GPT note: {text[:50]}")
    except RuntimeError as e:
        return WriteResponse(status="error", detail=str(e))

    return WriteResponse(status="success", detail="Note enregistrée dans la mémoire.")

# -----------------------------------------------------
#  Route 3: écriture d’un fichier dans un projet donné
# -----------------------------------------------------
@app.post("/write_file", response_model=WriteResponse)
async def write_file(req: WriteFileRequest):
    """
    Crée ou remplace un fichier (par ex. Markdown) dans projects/<projet>/fichiers/.
    """
    projet = req.project.strip()
    filename = req.filename.strip()
    content = req.content

    if not projet or not filename:
        raise HTTPException(status_code=400, detail="Les champs 'project' et 'filename' sont requis.")

    # Créer le dossier projet/fichiers si besoin
    project_slug = projet.lower().replace(" ", "_")
    base_path = Path("projects") / project_slug / "fichiers"
    try:
        base_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return WriteResponse(status="error", detail=f"Impossible de créer dossier {base_path}: {e}")

    file_path = base_path / filename
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return WriteResponse(
            status="error",
            detail=f"Erreur écriture du fichier {file_path}: {e}"
        )

    return WriteResponse(
        status="success",
        detail=f"Fichier créé/modifié: {file_path}",
        path=str(file_path)
    )
