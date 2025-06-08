import os
import subprocess
import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from git_utils import git_commit_push
from memory_lookup import search_memory
from memory_manager import query_memory

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
#  Endpoint de debug pour vérifier OPENAI_API_KEY
# ------------------------------------
@app.get("/check_env")
async def check_env():
    """
    Route de debug : affiche si OPENAI_API_KEY est défini et son préfixe.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"env_OK": False, "detail": "OPENAI_API_KEY n'est pas défini."}
    return {"env_OK": True, "OPENAI_API_KEY_prefix": api_key[:6] + "..."}

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
    project: str | None = None


class WriteFileRequest(BaseModel):
    project: str
    filename: str
    content: str

class WriteResponse(BaseModel):
    status: str
    detail: str | None = None
    path: str | None = None

class ReadNoteResponse(BaseModel):
    status: str
    results: list[str]

# ------------------------------------
#  POST /reprise  (DISCORD → Résumé Brut → Résumé GPT)
# ------------------------------------
@app.post("/reprise", response_model=RepriseResponse)
async def reprise_projet(req: RepriseRequest):
    projet = req.project.strip()
    if not projet:
        raise HTTPException(status_code=400, detail="Le champ 'project' ne peut pas être vide.")

    # 1) Déterminer la racine du projet
    base_path = Path(__file__).parent.parent

    # 2) Chemins vers les scripts Python
    discord_fetcher_script     = base_path / "scripts" / "discord_fetcher.py"
    project_resume_script      = base_path / "scripts" / "project_resume.py"
    project_resumer_gpt_script = base_path / "scripts" / "project_resumer_gpt.py"

    # Vérifier que tous les scripts existent
    for script_path in (
        discord_fetcher_script,
        project_resume_script,
        project_resumer_gpt_script
    ):
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
            cwd=str(base_path)
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

    # 5) Exécuter project_resumer_gpt.py <project> en capturant stdout/stderr
    try:
        process = subprocess.run(
            ["python", str(project_resumer_gpt_script), projet],
            capture_output=True,
            text=True,
            cwd=str(base_path)
        )
        if process.returncode != 0:
            detail = (
                f"Erreur project_resumer_gpt.py (code {process.returncode}):\n"
                f"STDOUT:\n{process.stdout}\n"
                f"STDERR:\n{process.stderr}"
            )
            return RepriseResponse(status="error", detail=detail)
    except Exception as e:
        return RepriseResponse(
            status="error",
            detail=f"Exception lors de l’appel à project_resumer_gpt.py : {repr(e)}"
        )

    # 6) Récupérer le dernier fichier resume_gpt_*.md
    project_slug  = projet.lower().replace(" ", "_")
    resume_folder = base_path / "projects" / project_slug / "resume"

    if not resume_folder.exists():
        return RepriseResponse(
            status="error",
            detail=f"Aucun dossier 'resume' pour le projet {projet}."
        )

    all_resumes = sorted(
        resume_folder.glob("resume_gpt_*.md"),
        key=lambda f: f.stat().st_mtime
    )
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
#  POST /write_note  (enregistrement direct + journal mimétique)
# ------------------------------------
@app.post("/write_note", response_model=WriteResponse)
async def write_note(req: WriteNoteRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Le champ 'text' ne peut pas être vide.")

    project_slug = req.project.strip().lower().replace(" ", "_") or "sentra_core"

    # 1) Chemin vers la racine du projet
    script_dir   = Path(__file__).resolve().parent   # …/scripts
    project_root = script_dir.parent                  # …/SENTRA_CORE_MEM_merged
    memory_dir   = project_root / "memory"            # …/memory
    memory_dir.mkdir(parents=True, exist_ok=True)     # crée le dossier si nécessaire
    memory_file  = memory_dir / "sentra_memory.json"  # …/memory/sentra_memory.json

    # 2) Préparer l'entrée JSON pour sentra_memory.json
    entry = {
        "type": "note",
        "text": text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    }

    try:
        # 3) Charger la mémoire existante (liste JSON)
        if memory_file.exists():
            try:
                memory = json.loads(memory_file.read_text(encoding="utf-8"))
                if not isinstance(memory, list):
                    memory = []
            except json.JSONDecodeError:
                memory = []
        else:
            memory = []
        # 4) Ajouter l'entrée puis réécrire complètement
        memory.append(entry)
        memory_file.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec d’écriture de la note : {repr(e)}")

    # 4) Journal mimétique Z_MEMORIAL.md

        project_slug = req.project.strip().lower().replace(" ", "_")or "sentra_core"

    memorial_dir  = project_root / "projects" / project_slug / "fichiers"
    memorial_dir.mkdir(parents=True, exist_ok=True)

    memorial_file = memorial_dir / "Z_MEMORIAL.md"
    timestamp_md  = time.strftime("## %Y-%m-%d %H:%M:%S\n- ", time.localtime())

    try:
        with memorial_file.open("a", encoding="utf-8") as mf:
            mf.write(f"{timestamp_md}{text}\n\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Note ajoutée au JSON, mais échec du journal Markdown : {repr(e)}")

    # 5) Mémoire markdown spécifique au projet si project fourni
    extra_files = [memory_file, memorial_file]
    if req.project:
        memoire_file = memorial_dir / f"memoire_{project_slug}.md"
        if not memoire_file.exists():
            memoire_file.touch()
        try:
            with memoire_file.open("a", encoding="utf-8") as mf:
                mf.write(f"{timestamp_md}{text}\n\n")
            extra_files.append(memoire_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Échec écriture memoire_{project_slug}.md : {repr(e)}")

    try:
    git_commit_push(extra_files, f"GPT note ({project_slug}): {text[:50]}")

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return WriteResponse(status="success", detail="Note enregistrée dans la mémoire.")

# ------------------------------------
#  GET /get_notes  (affichage de sentra_memory.json)
# ------------------------------------
@app.get("/get_notes")
async def get_notes():
    """
    Renvoie en texte brut le contenu complet de memory/sentra_memory.json.
    """
    script_dir   = Path(__file__).resolve().parent   # …/scripts
    project_root = script_dir.parent                  # …/SENTRA_CORE_MEM_merged
    memory_file  = project_root / "memory" / "sentra_memory.json"

    if not memory_file.exists():
        return Response(content="", media_type="text/plain")

    try:
        content = memory_file.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de lire le fichier : {repr(e)}")

    return Response(content=content, media_type="text/plain")

# ------------------------------------
#  GET /read_note  (recherche simple dans la mémoire)
# ------------------------------------
@app.get("/read_note", response_model=ReadNoteResponse)
async def read_note(term: str = "", limit: int = 5):
    try:
        if term:
            results = search_memory(term, max_results=limit)
        else:
            recent = query_memory(limit)
            results = [f"- [{e.get('timestamp','')}] {e.get('text','')}" for e in recent]
        return ReadNoteResponse(status="success", results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture mémoire : {repr(e)}")

# ------------------------------------
#  GET /get_memorial  (affichage de Z_MEMORIAL.md)
# ------------------------------------
@app.get("/get_memorial")
async def get_memorial(project: str = "sentra_core"):
    """
    Renvoie en texte brut le contenu de projects/<projet>/fichiers/Z_MEMORIAL.md.
    """
    script_dir   = Path(__file__).resolve().parent   # …/scripts
    project_root = script_dir.parent                  # …/SENTRA_CORE_MEM_merged
    project_slug = project.strip().lower().replace(" ", "_") or "sentra_core"
    memorial_file = project_root / "projects" / project_slug / "fichiers" / "Z_MEMORIAL.md"

    if not memorial_file.exists():
        return Response(content="Z_MEMORIAL.md non trouvé", media_type="text/plain")

    try:
        content = memorial_file.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de lire le fichier : {repr(e)}")

    return Response(content=content, media_type="text/plain")

# ------------------------------------
#  POST /write_file
# ------------------------------------
@app.post("/write_file", response_model=WriteResponse)
async def write_file(req: WriteFileRequest):
    projet   = req.project.strip()
    filename = req.filename.strip()
    contenu  = req.content

    if not projet or not filename:
        raise HTTPException(status_code=400, detail="Les champs 'project' et 'filename' sont requis.")

    base_path        = Path(__file__).parent.parent
    project_slug     = projet.lower().replace(" ", "_")
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

    try:
        git_commit_push([file_path], f"GPT file update ({project_slug}): {filename}")
    except RuntimeError as e:
        return WriteResponse(status="error", detail=str(e))

    return WriteResponse(
        status="success",
        detail=f"Fichier créé/modifié : {file_path}",
        path=str(file_path)
    )
