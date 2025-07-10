import json
from datetime import datetime
from pathlib import Path

# ─── Compression glyphique : stub si le module n’existe pas ───
try:
    from zmem_encoder import encode_zmem
except ImportError:

    def encode_zmem(*args, **kwargs):
        # Stub : ne fait rien, évite le crash si zmem_encoder absent
        pass


# ─────────────────────────────────────────────
#  FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────
def compress_entry(entry):
    """Raccourci visuel d’une entrée (pour logs éventuels)."""
    contenu = entry.get("contenu", "") if isinstance(entry, dict) else str(entry)
    return contenu if len(contenu) <= 20 else contenu[:10] + "..." + contenu[-10:]


# ─────────────────────────────────────────────
#  FONCTION PRINCIPALE : save_note_from_text
# ─────────────────────────────────────────────
def save_note_from_text(note_text: str):
    """
    1. Compresse la note (glyphique) dans /memory_zia/
    2. Stocke l’entrée dans /memory/sentra_memory.json (liste JSON)
    """
    # --- Compression glyphique (optionnelle) ---
    ctx_tag = datetime.now().strftime("¤SCM/%y%m%d.MEM_AUTO")
    content = f"<note>{note_text}</note>"
    zdir = Path("memory_zia")
    zdir.mkdir(exist_ok=True)

    try:
        encode_zmem(  # si encode_zmem n’existe pas encore,
            content=content,  # commente ce bloc temporairement
            ctx_tag=ctx_tag,
            zlib_txt_out=zdir / f"auto_{ctx_tag}.zlib.txt",
            zlib_bin_out=zdir / f"auto_{ctx_tag}.l64.b",
            zmem_src_out=zdir / f"auto_{ctx_tag}.src",
            zmem_bin_out=zdir / f"auto_{ctx_tag}.zmem",
            update_dict_path=zdir / "mem_dict.json",
        )
    except Exception as e:
        print(f"⚠️  Compression zmem ignorée : {e}")

    # --- Écriture mémoire persistante (liste JSON) ---
    project_root = Path(__file__).resolve().parent.parent  # …/SENTRA_CORE_MEM_merged
    mem_file = project_root / "memory" / "sentra_memory.json"
    mem_file.parent.mkdir(parents=True, exist_ok=True)

    # Charger l’existant
    if mem_file.exists():
        try:
            with mem_file.open("r", encoding="utf-8") as f:
                memory = json.load(f)
                if not isinstance(memory, list):
                    memory = []
        except json.JSONDecodeError:
            memory = []
    else:
        memory = []

    # Ajouter la nouvelle entrée
    memory.append(
        {
            "type": "note",
            "text": note_text,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
    )

    # Réécrire le fichier complet
    with mem_file.open("w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

    print("🧠 Note enregistrée dans la mémoire JSON.")


# ─────────────────────────────────────────────
#  TEST MANUEL (exécution directe)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    save_note_from_text("Note de test depuis memory_agent.py")
