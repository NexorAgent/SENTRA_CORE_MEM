import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

# ------------------------------------
#  Création de l’application FastAPI
# ------------------------------------
app = FastAPI(
    title="Sentra Memory Plugin API",
    version="1.1.0",
    description="API pour piloter la reprise et l'écriture dans un projet SENTRA (Discord ↔ résumé GPT, notes, fichiers)."
)

# ------------------------------------
#  Route statique pour servir ai-plugin.json
# ------------------------------------
@app.get("/ai-plugin.json", include_in_schema=False)
async def get_ai_plugin():
    manifest_path = Path(__file__).parent.parent / "ai-plugin.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="ai-plugin.json introuvable")
    return FileResponse(path=str(manifest_path), media_type="application/json")

# ------------------------------------
#  Route statique pour servir logo.png
# ------------------------------------
@app.get("/logo.png", include_in_schema=False)
async def get_logo():
    logo_path = Path(__file__).parent.parent / "logo.png"
    if logo_path.exists():
        return FileResponse(path=str(logo_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo non trouvé")

# ------------------------------------
#  Modèles de requête / réponse
# ------------------------------------
class RepriseRequest(BaseModel):
    project: str

class RepriseResponse(BaseModel):
    status: str
    resume_path: str | None = None
    resume_content: str | None = None
    detail: str | None = None

class WriteNoteRequest(BaseModel):
    text: str

class WriteFileRequest(BaseModel):
    project: str
    filename: str
    content: str

class WriteResponse(BaseModel):
    status: str
    detail: str | None = None
    path: str | None = None

# ------------------------------------
#  POST /reprise  (DISCORD →Résumé Brut→Résumé GPT)
# ------------------------------------
@app.post("/reprise", response_model=RepriseResponse)
async def reprise_projet(req: RepriseRequest):
    projet = req.project.strip()
    if not projet:
        raise HTTPException(status_code=400, detail="Le champ 'project' ne peut pas être vide.")

    # 1) Déterminer la racine du projet (SENTRA_CORE_MEM_merged)
    #    __file__ vaut ".../SENTRA_CORE_MEM_merged/scripts/api_sentra.py"
    base_path = Path(__file__).parent.parent

    # 2) Chemins absolus vers les scripts Python
    discord_fetcher_script   = base_path / "scripts" / "discord_fetcher.py"
    project_resume_script    = base_path / "scripts" / "project_resume.py"
    project_resumer_gpt_script = base_path / "scripts" / "project_resumer_gpt.py"

    # Vérification rapide : les fichiers existent-ils ?
    for script_path in (discord_fetcher_script, project_resume_script, project_resumer_gpt_script):
        if not script_path.exists():
            return RepriseResponse(
                status="error",
                detail=f"Script manquant : {script_path.name}"
            )

    # 3) Exécuter discord_fetcher.py <project>
    try:
        subprocess.run(
            ["python", str(discord_fetcher_script), projet],
            check=True,
            cwd=str(base_path)  # on force le cwd sur la racine du projet
        )
    except subprocess.CalledProcessError as e:
        return RepriseResponse(
            status="error",
            detail=f"Échec discord_fetcher.py : {e.stderr or e}"
        )

    # 4) Exécuter project_resume.py <project>
    try:
        subprocess.run(
            ["python", str(project_resume_script), projet],
            check=True,
            cwd=str(base_path)
        )
    except subprocess.CalledProcessError as e:
        return RepriseResponse(
            status="error",
            detail=f"Échec project_resume.py : {e.stderr or e}"
        )

    # 5) Exécuter project_resumer_gpt.py <project>
    try:
        subprocess.run(
            ["python", str(project_resumer_gpt_script), projet],
            check=True,
            cwd=str(base_path)
        )
    except subprocess.CalledProcessError as e:
        return RepriseResponse(
            status="error",
            detail=f"Échec project_resumer_gpt.py : {e.stderr or e}"
        )

    # 6) Récupérer le dernier fichier resume_gpt_*.md généré
    project_slug = projet.lower().replace(" ", "_")
    resume_folder = base_path / "projects" / project_slug / "resume"

    if not resume_folder.exists():
        return RepriseResponse(
            status="error",
            detail=f"Aucun dossier 'resume' pour le projet {projet}."
        )

    all_resumes = sorted(resume_folder.glob("resume_gpt_*.md"), key=lambda f: f.stat().st_mtime)
    if not all_resumes:
        return RepriseResponse(
            status="error",
            detail="Aucun fichier 'resume_gpt_*.md' trouvé."
        )

    last_resume = all_resumes[-1]
    try:
        content = last_resume.read_text(encoding="utf-8")
    except Exception as e:
        return RepriseResponse(
            status="error",
            detail=f"Impossible de lire le fichier {last_resume.name} : {e}"
        )

    return RepriseResponse(
        status="success",
        resume_path=str(last_resume),
        resume_content=content
    )

# ------------------------------------
#  POST /write_note
# ------------------------------------
@app.post("/write_note", response_model=WriteResponse)
async def write_note(req: WriteNoteRequest):
    from memory_agent import save_note_from_text  # ou ajustez selon l’import réel

    texte = req.text.strip()
    if not texte:
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    try:
        save_note_from_text(texte)
    except Exception as e:
        return WriteResponse(status="error", detail=f"Erreur write_note : {e}")

    return WriteResponse(status="success", detail="Note enregistrée dans la mémoire.")

# ------------------------------------
#  POST /write_file
# ------------------------------------
@app.post("/write_file", response_model=WriteResponse)
async def write_file(req: WriteFileRequest):
    projet = req.project.strip()
    filename = req.filename.strip()
    contenu = req.content

    if not projet or not filename:
        raise HTTPException(status_code=400, detail="Les champs 'project' et 'filename' sont requis.")

    base_path = Path(__file__).parent.parent
    project_slug = projet.lower().replace(" ", "_")
    dossier_fichiers = base_path / "projects" / project_slug / "fichiers"

    try:
        dossier_fichiers.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return WriteResponse(status="error", detail=f"Impossible de créer le dossier {dossier_fichiers} : {e}")

    file_path = dossier_fichiers / filename
    try:
        file_path.write_text(contenu, encoding="utf-8")
    except Exception as e:
        return WriteResponse(status="error", detail=f"Erreur écriture du fichier {file_path} : {e}")

    return WriteResponse(
        status="success",
        detail=f"Fichier créé/modifié : {file_path}",
        path=str(file_path)
    )
