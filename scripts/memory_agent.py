from datetime import datetime
import os
import json
from pathlib import Path
from zmem_encoder import encode_zmem

# Fonction utilitaire : si nécessaire, compresse un champ pour affichage

def compress_entry(entry):
    if isinstance(entry, dict):
        contenu = entry.get('contenu', '')
    else:
        contenu = str(entry)
    if len(contenu) <= 20:
        return contenu
    return contenu[:10] + "..." + contenu[-10:]

# Fonction publique appelée depuis le dispatcher ou Discord
# Elle effectue deux actions :
# 1. Compression glyphique via encode_zmem (dossier 'memory_zia/')
# 2. Enregistrement en JSON linéaire dans 'memory/sentra_memory.json'

def save_note_from_text(note_text: str):
    # --- Partie compression glyphique (zmem) ---
    ctx_tag = datetime.now().strftime("¤SCM/%y%m%d.MEM_AUTO")
    content = f"<note>{note_text}</note>"
    # Construire chemins de sortie dans 'memory_zia/'
    zlib_txt_out = f"memory_zia/auto_{ctx_tag}.zlib.txt"
    zlib_bin_out = f"memory_zia/auto_{ctx_tag}.l64.b"
    zmem_src_out = f"memory_zia/auto_{ctx_tag}.src"
    zmem_bin_out = f"memory_zia/auto_{ctx_tag}.zmem"
    mem_dict_path = "memory_zia/mem_dict.json"
    # Créer le dossier 'memory_zia/' si nécessaire
    os.makedirs(os.path.dirname(zlib_txt_out), exist_ok=True)
    # Appel à encode_zmem
    try:
        encode_zmem(
            content=content,
            ctx_tag=ctx_tag,
            zlib_txt_out=zlib_txt_out,
            zlib_bin_out=zlib_bin_out,
            zmem_src_out=zmem_src_out,
            zmem_bin_out=zmem_bin_out,
            update_dict_path=mem_dict_path
        )
    except Exception as e:
        print(f"❌ Erreur lors de la compression zmem : {e}")

    print(f"🧠 Mémoire ZIA enregistrée depuis Discord : {note_text}")

    # --- Partie écriture JSON linéaire persistante ---
    # Déterminer le chemin vers le dossier racine du projet
    script_dir = Path(__file__).resolve().parent        # .../scripts
    project_root = script_dir.parent                   # .../SENTRA_CORE_MEM_merged
    memory_dir = project_root / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file = memory_dir / "sentra_memory.json"

    entry = {
        "type": "note",
        "text": note_text,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }
    try:
        with memory_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"❌ Erreur écriture mémoire JSON : {e}")
