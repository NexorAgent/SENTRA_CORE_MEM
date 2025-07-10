# SENTRA_REGEN_CORE.py – Régénérateur adaptatif SENTRA (v0.1)

import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
MEMORIAL = ROOT / "Z_MEMORIAL.md"
EVOL_LOG = ROOT / "Z.EVOL_MIME"

REGEN_TARGETS = {
    "Z_PROMPT_CODEX_GITOPS.txt": "# Prompt CODEX GitOps (régénéré)",
    "Z_PROMPT_CODEX_REGEN.txt": "# Prompt CODEX Regen (régénéré)",
    "SENTRA_OATH.md": "# Charte SENTRA OATH (régénérée)",
    "Z_PLANNING.md": "# Planning par défaut (régénéré)",
    "glyph_dict.json": "{}",
}


def log_event(entry: str):
    timestamp = datetime.now().isoformat()
    with open(EVOL_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {entry}\n")


def scan_targets():
    print("🔍 Scan des fichiers critiques...")
    for filename in REGEN_TARGETS:
        target_path = (
            ROOT / filename
            if not filename.startswith("Z_PROMPT")
            else PROMPTS_DIR / filename
        )
        if not target_path.exists():
            print(f"❌ Manquant : {target_path}")
        else:
            print(f"✅ Présent : {target_path}")


def regen_targets():
    print("♻️ Régénération des fichiers manquants...")
    for filename, content in REGEN_TARGETS.items():
        target_path = (
            ROOT / filename
            if not filename.startswith("Z_PROMPT")
            else PROMPTS_DIR / filename
        )
        if not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"🆕 Fichier régénéré : {target_path}")
            log_event(f"REGEN: {filename} recréé automatiquement")


def full_cycle():
    scan_targets()
    regen_targets()
    print("✅ Cycle complet terminé")


def main():
    parser = argparse.ArgumentParser(
        description="SENTRA_REGEN_CORE - Régénération adaptative IA"
    )
    parser.add_argument("--scan", action="store_true", help="Scanner les fichiers clés")
    parser.add_argument(
        "--regen", action="store_true", help="Régénérer les fichiers manquants"
    )
    parser.add_argument(
        "--full", action="store_true", help="Faire un scan + régénération + log"
    )
    args = parser.parse_args()

    if args.scan:
        scan_targets()
    elif args.regen:
        regen_targets()
    elif args.full:
        full_cycle()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
