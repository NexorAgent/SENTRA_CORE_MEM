import os
import subprocess
import json
import time
from pathlib import Path
from app.routes.correction import router as correction_router

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

from fastapi import FastAPI, HTTPException, Response, Query  # <--- AJOUTE Query ici
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .git_utils import git_commit_push
from .memory_lookup import search_memory
from .memory_manager import query_memory

def liste_suggestions(path):
    """
    Retourne la liste triée des fichiers/dossiers dans le dossier parent existant le plus proche.
    """
    current = Path(path)
    while not current.exists() and current != current.parent:
        current = current.parent
    try:
        return sorted([f.name for f in current.iterdir()])
    except Exception:
        return []


def suggest_near(target, candidates):
    """
    Propose les fichiers proches du nom demandé (par inclusion du tronc du nom).
    """
    base = target.split('.')[0]
    return [f for f in candidates if base in f]

# ------------------------------------
#  Création de l’application FastAPI
# ------------------------------------
app = FastAPI(
    title="Sentra Memory Plugin API",
    version="1.1.0",
    description="API pour piloter la reprise et l'écriture dans un projet SENTRA (Discord ↔ résumé GPT, notes, fichiers)."
)
app.include_router(correction_router)

# ------------------------------------
#  Route statique pour servir ai-plugin.json
# ------------------------------------
@app.get("/ai-plugin.json", include_in_schema=False)
async def get_ai_plugin():
    manifest_path = BASE_DIR / "ai-plugin.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="ai-plugin.json introuvable")
    return FileResponse(path=str(manifest_path), media_type="application/json")

# ------------------------------------
#  Route statique pour servir logo.png
# ------------------------------------
@app.get("/logo.png", include_in_schema=False)
async def get_logo():
    logo_path = BASE_DIR / "logo.png"
    if logo_path.exists():
        return FileResponse(path=str(logo_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo non trouvé")

# ------------------------------------
#  Notice légale / licence
# ------------------------------------
@app.get("/legal", include_in_schema=False)
async def legal_notice():
    """Retourne le contenu de NOTICE.md ou un texte de licence."""
    notice_path = BASE_DIR / "NOTICE.md"
    if notice_path.exists():
        return FileResponse(path=str(notice_path), media_type="text/markdown")
    return Response(
        content="SENTRA Memory Plugin - MIT License \u00a9 2025 SENTRA CORE",
        media_type="text/plain",
    )

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

class DeleteFileRequest(BaseModel):
    path: str
    validate_before_delete: bool = True

class MoveFileRequest(BaseModel):
    src: str
    dst: str

class ArchiveFileRequest(BaseModel):
    path: str
    archive_dir: str

class FileActionResponse(BaseModel):
    status: str
    detail: str | None = None
    path: str | None = None

class WriteResponse(BaseModel):
    status: str
    detail: str | None = None
    path: str | None = None
    suggestions: list[str] = []

class ReadNoteResponse(BaseModel):
    status: str
    results: list[str]
    suggestions: list[str] = []

class ListFilesResponse(BaseModel):
    status: str
    detail: str | None = None
    files: list[str]

class SearchResponse(BaseModel):
    status: str
    detail: str | None = None
    matches: list[str]

# Requests pour la gestion de fichiers existants

# ------------------------------------
#  POST /reprise  (DISCORD → Résumé Brut → Résumé GPT)
# ------------------------------------
@app.post("/reprise", response_model=RepriseResponse)
async def reprise_projet(req: RepriseRequest):
    projet = req.project.strip()
    if not projet:
        raise HTTPException(status_code=400, detail="Le champ 'project' ne peut pas être vide.")

    # 1) Déterminer la racine du projet
    base_path = BASE_DIR

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

    project_val = getattr(req, "project", None) or "sentra_core"
    project_slug = project_val.strip().lower().replace(" ", "_")
    # Calcul une seule fois du slug projet/clone
   
    # 1) Chemin vers la racine du projet
    memory_dir   = BASE_DIR / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file  = memory_dir / "sentra_memory.json"

    # 2) Préparer l'entrée JSON pour sentra_memory.json
    entry = {
        "type": "note",
        "text": text,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    }

    try:
        if memory_file.exists():
            try:
                memory = json.loads(memory_file.read_text(encoding="utf-8"))
                if not isinstance(memory, list):
                    memory = []
            except json.JSONDecodeError:
                memory = []
        else:
            memory = []
        memory.append(entry)
        memory_file.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec d’écriture de la note : {repr(e)}")

    # 3) Journal mimétique Z_MEMORIAL.md
    memorial_dir  = BASE_DIR / "projects" / project_slug / "fichiers"
    memorial_dir.mkdir(parents=True, exist_ok=True)

    memorial_file = memorial_dir / "Z_MEMORIAL.md"
    timestamp_md  = time.strftime("## %Y-%m-%d %H:%M:%S\n- ", time.localtime())

    try:
        with memorial_file.open("a", encoding="utf-8") as mf:
            mf.write(f"{timestamp_md}{text}\n\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Note ajoutée au JSON, mais échec du journal Markdown : {repr(e)}")

    # 4) Mémoire markdown spécifique au projet si project fourni
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
#  GET /read_note  (lecture intelligente fichier + mémoire)
# ------------------------------------
@app.get("/read_note", response_model=ReadNoteResponse)
async def read_note(term: str = "", limit: int = 5, filepath: str = None):
    """
    Lecture intelligente universelle :
    - Si 'filepath' fourni, lire tout fichier texte (md/txt) → status success si contenu, error sinon.
    - Sinon, recherche classique mémoire IA.
    - Toujours status explicite, suggestions en cas d’erreur.
    """
    if filepath:
        file_path = BASE_DIR / filepath
        parent = file_path.parent
        candidates = liste_suggestions(parent)
        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                if content.strip():
                    return ReadNoteResponse(
                        status="success",
                        results=[content],
                        suggestions=[]
                    )
                else:
                    return ReadNoteResponse(
                        status="error",
                        results=[f"Fichier '{filepath}' vide."],
                        suggestions=[]
                    )
            except Exception as e:
                return ReadNoteResponse(
                    status="error",
                    results=[f"Erreur de lecture de {filepath}: {e}"],
                    suggestions=candidates
                )
        else:
            near = suggest_near(file_path.name, candidates)
            return ReadNoteResponse(
                status="error",
                results=[f"Fichier '{filepath}' introuvable."],
                suggestions=near if near else candidates
            )
    # Fallback : mémoire IA classique
    try:
        if term:
            results = search_memory(term, max_results=limit)
        else:
            recent = query_memory(limit)
            results = [f"- [{e.get('timestamp','')}] {e.get('text','')}" for e in recent]
        if not results:
            return ReadNoteResponse(
                status="error",
                results=["Aucune note trouvée dans la mémoire IA."],
                suggestions=[]
            )
        return ReadNoteResponse(status="success", results=results, suggestions=[])
    except Exception as e:
        return ReadNoteResponse(
            status="error",
            results=[f"Erreur lecture mémoire : {e}"],
            suggestions=[]
        )

# ------------------------------------
#  POST /movefile
# ------------------------------------
@app.post("/move_file", response_model=WriteResponse)
async def move_file(req: MoveFileRequest):
    if ".." in req.src or ".." in req.dst:
        return WriteResponse(
            status="error",
            detail="Invalid path",
            path=None,
            suggestions=[]
        )
    src_path = BASE_DIR / req.src
    dst_path = BASE_DIR / req.dst

    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.rename(dst_path)
    except FileNotFoundError:
        candidates = liste_suggestions(src_path.parent)
        near = suggest_near(src_path.name, candidates)
        return WriteResponse(
            status="error",
            detail=f"Fichier source introuvable : {src_path}",
            path=None,
            suggestions=near if near else candidates
        )
    except PermissionError as e:
        return WriteResponse(
            status="error",
            detail=f"Permission refusée : {e}",
            path=None,
            suggestions=[]
        )
    except Exception as e:
        return WriteResponse(
            status="error",
            detail=f"Erreur déplacement {src_path} -> {dst_path} : {e}",
            path=None,
            suggestions=[]
        )

    try:
        git_commit_push([src_path, dst_path], f"GPT move: {src_path} -> {dst_path}")
    except RuntimeError as e:
        return WriteResponse(
            status="error",
            detail=str(e),
            path=None,
            suggestions=[]
        )

    return WriteResponse(
        status="success",
        detail=f"Fichier déplacé : {dst_path}",
        path=str(dst_path),
        suggestions=[]
    )


# ------------------------------------
#  POST /write_file
# ------------------------------------

@app.post("/write_file", response_model=WriteResponse)
async def write_file(req: WriteFileRequest):
    projet   = req.project.strip()
    filename = req.filename.strip()
    contenu  = req.content

    if not projet or not filename:
        return WriteResponse(
            status="error",
            detail="Les champs 'project' et 'filename' sont requis.",
            path=None,
            suggestions=[]
        )

    if ".." in filename:
        return WriteResponse(
            status="error",
            detail="Invalid filename",
            path=None,
            suggestions=[]
        )

    project_slug = projet.lower().replace(" ", "_")
    file_path = BASE_DIR / "projects" / project_slug / "fichiers" / filename

    # Création automatique du dossier cible
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        suggestions = liste_suggestions(file_path.parent.parent)
        return WriteResponse(
            status="error",
            detail=f"Impossible de créer le dossier {file_path.parent} : {e}",
            path=None,
            suggestions=suggestions
        )

    try:
        file_path.write_text(contenu, encoding="utf-8")
    except Exception as e:
        suggestions = liste_suggestions(file_path.parent)
        return WriteResponse(
            status="error",
            detail=f"Erreur écriture du fichier {file_path} : {e}",
            path=None,
            suggestions=suggestions
        )

    try:
        git_commit_push([file_path], f"GPT file update ({project_slug}): {filename}")
    except RuntimeError as e:
        return WriteResponse(status="error", detail=str(e), path=None, suggestions=[])

    return WriteResponse(
        status="success",
        detail=f"Fichier créé/modifié : {file_path}",
        path=str(file_path),
        suggestions=[]
    )

# ------------------------------------
#  GET /get_memorial  (affichage de Z_MEMORIAL.md)
# ------------------------------------
@app.get("/get_memorial")
async def get_memorial(project: str = "sentra_core"):
    """
    Renvoie en texte brut le contenu de projects/<projet>/fichiers/Z_MEMORIAL.md.
    """
    project_slug = project.strip().lower().replace(" ", "_") or "sentra_core"
    memorial_file = BASE_DIR / "projects" / project_slug / "fichiers" / "Z_MEMORIAL.md"

    if not memorial_file.exists():
        return Response(content="Z_MEMORIAL.md non trouvé", media_type="text/plain")

    try:
        content = memorial_file.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de lire le fichier : {repr(e)}")

    return Response(content=content, media_type="text/plain")


# ------------------------------------
#  POST /archive_file
# ------------------------------------
 
@app.post("/archive_file", response_model=WriteResponse)
async def archive_file(req: ArchiveFileRequest):
    if ".." in req.path or ".." in req.archive_dir:
        return WriteResponse(
            status="error",
            detail="Invalid path",
            path=None,
            suggestions=[]
        )
    src_path = BASE_DIR / req.path
    archive_dir = BASE_DIR / req.archive_dir
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        suggestions = liste_suggestions(archive_dir.parent)
        return WriteResponse(
            status="error",
            detail=f"Impossible de créer le dossier {archive_dir} : {e}",
            path=None,
            suggestions=suggestions
        )
    dest_path = archive_dir / src_path.name

    try:
        src_candidates = liste_suggestions(src_path.parent)
        src_near = suggest_near(src_path.name, src_candidates)
        src_path.rename(dest_path)
    except FileNotFoundError:
        # Suggestions fuzzy en priorité
        return WriteResponse(
            status="error",
            detail=f"Fichier introuvable : {src_path}",
            path=None,
            suggestions=src_near if src_near else src_candidates
        )
    except PermissionError as e:
        return WriteResponse(
            status="error",
            detail=f"Permission refusée : {e}",
            path=None,
            suggestions=[]
        )
    except Exception as e:
        return WriteResponse(
            status="error",
            detail=f"Erreur archivage {src_path} : {e}",
            path=None,
            suggestions=[]
        )

    try:
        git_commit_push([src_path, dest_path], f"GPT archive: {src_path.name}")
    except RuntimeError as e:
        return WriteResponse(
            status="error",
            detail=str(e),
            path=None,
            suggestions=[]
        )

    return WriteResponse(
        status="success",
        detail=f"Fichier archivé : {dest_path}",
        path=str(dest_path),
        suggestions=[]
    )


# ------------------------------------
#  GET /list_files
# ------------------------------------
@app.get("/list_files", response_model=ListFilesResponse)
async def list_files(dir: str, pattern: str = "*"):
 
    p = Path(dir)
    try:
        files = [str(f) for f in p.glob(pattern)]
        return ListFilesResponse(
            status="success",
            detail=f"{len(files)} file(s) found",
            files=files,
        )
    except Exception as e:
        return ListFilesResponse(status="error", detail=str(e), files=[])

    if ".." in dir:
        raise HTTPException(status_code=400, detail="Invalid path")
    p = BASE_DIR / dir
    files = [str(f) for f in p.glob(pattern)]
    return {"files": files}
 

# ------------------------------------
#  GET /search
# ------------------------------------
@app.get("/search", response_model=SearchResponse)
async def search_files(term: str, dir: str):
    if ".." in dir:
        raise HTTPException(status_code=400, detail="Invalid path")
    base = BASE_DIR / dir
    results = []
    for f in base.rglob("*"):
        if f.is_file():
            try:
                if term.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
                    results.append(str(f))
            except Exception:
                continue
    return SearchResponse(
        status="success",
        detail=f"{len(results)} match(es)",
        matches=results,
    )
    
  # ------------------------------------
#  GET /explore
# ------------------------------------
@app.get("/explore", tags=["monitoring"])
async def explore(
    project: str = Query(..., description="Nom du projet"),
    path: str = Query("/", description="Chemin relatif à explorer (défaut: racine du projet)")
):
    """
    Explore l'arborescence d'un projet et retourne la structure récursive à partir de 'path'.
    """
    base_dir = BASE_DIR / "projects" / project.strip().lower()
    target_path = (base_dir / path.lstrip("/")).resolve()

    # Sécurité : le chemin doit rester dans le dossier projet
    if not str(target_path).startswith(str(base_dir)):
        raise HTTPException(status_code=400, detail="Chemin hors du projet interdit.")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Dossier/fichier introuvable.")

    def scan_dir(p):
        items = []
        for child in sorted(p.iterdir()):
            if child.is_dir():
                items.append({
                    "name": child.name,
                    "type": "dir",
                    "children": scan_dir(child)
                })
            else:
                items.append({
                    "name": child.name,
                    "type": "file"
                })
        return items

    children = []
    if target_path.is_dir():
        children = scan_dir(target_path)
    else:
        children = [{"name": target_path.name, "type": "file"}]

    return {
        "project": project,
        "path": str(path),
        "children": children
    }

# ------------------------------------
#  POST /delete_file (suppression tolérante)
# ------------------------------------
@app.post("/delete_file", response_model=WriteResponse)
async def delete_file(req: DeleteFileRequest):
    if ".." in req.path:
        return WriteResponse(
            status="error",
            detail="Invalid path",
            path=None,
            suggestions=[]
        )
    file_path = BASE_DIR / req.path
    try:
        file_path.unlink()
    except FileNotFoundError:
        candidates = liste_suggestions(file_path.parent)
        near = suggest_near(file_path.name, candidates)
        return WriteResponse(
            status="error",
            detail=f"Fichier introuvable : {file_path}",
            path=None,
            suggestions=near if near else candidates
        )
    except PermissionError as e:
        return WriteResponse(
            status="error",
            detail=f"Permission refusée : {e}",
            path=None,
            suggestions=[]
        )
    except Exception as e:
        return WriteResponse(
            status="error",
            detail=f"Erreur suppression du fichier {file_path} : {e}",
            path=None,
            suggestions=[]
        )

    try:
        git_commit_push([file_path], f"GPT delete: {file_path.name}")
    except RuntimeError as e:
        return WriteResponse(
            status="error",
            detail=str(e),
            path=None,
            suggestions=[]
        )

    return WriteResponse(
        status="success",
        detail=f"Fichier supprimé : {file_path}",
        path=str(file_path),
        suggestions=[]
    )

# === SENTRA CORE MEM — ROUTES PUBLIQUES INTELLIGENTES ===

from fastapi.responses import JSONResponse, PlainTextResponse

@app.get("/", tags=["monitoring"])
async def home():
    return JSONResponse(
        content={"message": "✅ API SENTRA_CORE_MEM active. Bienvenue sur le noyau IA local."}
    )

@app.get("/status", tags=["monitoring"])
async def status():
    return {
        "status": "🟢 OK",
        "project": "SENTRA_CORE_MEM",
        "version": "v0.4",
        "agents": ["markdown", "notion", "discord", "glyph", "scheduler"]
    }

@app.get("/version", tags=["monitoring"])
async def get_version():
    changelog_path = BASE_DIR / "CHANGELOG.md"
    if changelog_path.exists():
        with open(changelog_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read(), media_type="text/plain")
    return JSONResponse(content={"error": "CHANGELOG.md non trouvé"}, status_code=404)

@app.get("/readme", tags=["monitoring"])
async def get_readme():
    readme_path = BASE_DIR / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read(), media_type="text/plain")
    return JSONResponse(content={"error": "README.md non trouvé"}, status_code=404)

@app.get("/logs/latest", tags=["logs"])
async def get_latest_logs():
    log_path = BASE_DIR / "logs" / "execution_log.txt"
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return {"latest": lines[-10:]}
    return JSONResponse(content={"error": "Aucun log trouvé"}, status_code=404)

@app.get("/agents", tags=["monitoring"])
async def list_agents():
    return {
        "active_agents": [
            "markdown", "notion", "discord", "glyph", "scheduler"
        ],
        "status": "🟢 tous actifs (dans le code)"
    }
