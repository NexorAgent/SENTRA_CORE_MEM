from pathlib import Path
import sys
import time
import subprocess

# ───────────────────────────────
# Chemins – racine du projet
# ───────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # …/SENTRA_CORE_MEM_merged
sys.path.insert(0, str(PROJECT_ROOT))

LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "execution_log.txt"


# ────────────────────────────────────────────
# Fonction utilitaire pour appeler un script
# ────────────────────────────────────────────

def run_script(python_script_path, *args):
    """
    Exécute le script Python situé à python_script_path avec la liste d'arguments args.
    Affiche stdout/stderr. Renvoie le code de retour (0 si OK).
    """
    cmd = [sys.executable, str(python_script_path)] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Afficher stdout et stderr
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {python_script_path} : {e}")
        return -1


# ───────────────────────────────────────────────
# Dispatcher du mode “langage naturel” (ancien comportement)
# ───────────────────────────────────────────────

def dispatcher(message: str):
    # S’assurer que Python peut trouver le module sentra.dispatcher
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from sentra.dispatcher import detect_intent_and_route
    except ImportError:
        return {"intent": "error", "réponse": "Erreur interne : dispatcher introuvable.", "glyph": "❌"}

    retour = detect_intent_and_route(message)
    intent = retour.get("intent", "unknown")
    reponse = retour.get("réponse", "")
    glyph = retour.get("glyph", "")

    # Log de l'intent
    try:
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {intent} -> {reponse}\n")
    except Exception as exc:
        print("❌ Impossible d'écrire dans le log :", exc)

    # Si intent de synchronisation, on appelle l'agent Notion
    if intent == "sync_notion":
        try:
            from scripts.agent_notion import run as run_sync
            run_sync()
            return {"intent": "sync_notion", "réponse": "✅ Synchronisation vers Notion effectuée.", "glyph": "✅"}
        except Exception as e:
            return {"intent": "error", "réponse": f"❌ Échec de la synchronisation : {e}", "glyph": "❌"}

    return retour


# ────────────────────────────────────────────
# Point d'entrée principal
# ────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        # Aucun argument CLI : mode langage naturel
        msg = "synchronisation mémoire"
        print(dispatcher(msg))
        sys.exit(0)

    subcmd = args[0].lower()

    # Cas "encode"
    if subcmd == "encode":
        input_path = None
        name = None
        i = 1
        while i < len(args):
            if args[i] in ("-i", "--input") and i + 1 < len(args):
                input_path = args[i + 1]
                i += 2
            elif args[i] in ("-n", "--name") and i + 1 < len(args):
                name = args[i + 1]
                i += 2
            else:
                i += 1

        if not input_path or not name:
            print("Usage: python sentra\\orchestrator.py encode --input <chemin> --name <nom_memo>")
            sys.exit(1)

        encoder_script = PROJECT_ROOT / "scripts" / "zmem_encoder.py"
        print(f"🔧 Lancement de l’encodage : fichier ={input_path}, nom ={name}")
        code = run_script(encoder_script, "-i", input_path, "-n", name)
        sys.exit(code)

    # Cas "load"
    elif subcmd == "load":
        name = None
        i = 1
        while i < len(args):
            if args[i] in ("-n", "--name") and i + 1 < len(args):
                name = args[i + 1]
                i += 2
            else:
                i += 1

        if not name:
            print("Usage: python sentra\\orchestrator.py load --name <nom_memo>")
            sys.exit(1)

        loader_script = PROJECT_ROOT / "scripts" / "zmem_loader.py"
        print(f"🔍 Lancement du chargement (load) de la mémoire : {name}")
        code = run_script(loader_script, name)
        sys.exit(code)

    # Cas "sync" en CLI :
    elif subcmd == "sync":
        target = None
        i = 1
        while i < len(args):
            if args[i] in ("-t", "--target") and i + 1 < len(args):
                target = args[i + 1].lower()
                i += 2
            else:
                i += 1

        if not target or target not in ("notion", "discord", "all"):
            print("Usage: python sentra\\orchestrator.py sync --target notion|discord|all")
            sys.exit(1)

        if target in ("notion", "all"):
            agent_notion_script = PROJECT_ROOT / "scripts" / "agent_notion.py"
            print("🔄 Synchronisation vers Notion…")
            run_script(agent_notion_script)
        if target in ("discord", "all"):
            discord_script = PROJECT_ROOT / "scripts" / "discord_bot.py"
            print("🔄 Synchronisation vers Discord…")
            run_script(discord_script)

        sys.exit(0)

    # Cas "report"
    elif subcmd == "report":
        report_date = None
        i = 1
        while i < len(args):
            if args[i] in ("-d", "--date") and i + 1 < len(args):
                report_date = args[i + 1]
                i += 2
            else:
                i += 1

        if not report_date:
            print("Usage: python sentra\\orchestrator.py report --date YYYY-MM-DD")
            sys.exit(1)

        markdown_script = PROJECT_ROOT / "scripts" / "agent_markdown.py"
        print(f"📄 Génération de rapport pour la date : {report_date}")
        code = run_script(markdown_script, report_date)
        sys.exit(code)

    # Autres cas (langage naturel via dispatcher)
    else:
        msg = " ".join(args)
        result = dispatcher(msg)
        print(result)
        sys.exit(0)
