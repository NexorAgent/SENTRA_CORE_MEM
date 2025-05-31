# scripts/pipeline_traducteur.py
"""
Pipeline de traduction glyphique SENTRA
───────────────────────────────────────
1. Lit le fichier log passé en argument
2. Extrait les termes clés
3. Génère ou récupère un glyphe pour chacun puis met à jour `memory/glyph_dict.json`
4. Remplace chaque terme par son glyphe dans le texte
5. Écrit le résultat dans `logs/<nom>_translated.txt`
6. Appelle automatiquement `index_builder` pour mettre à jour l’index mémoire

🌐  Compatible Windows : aucun caractère non-CP1252 n’est envoyé à `print()`.
"""

from __future__ import annotations
import sys, re, zlib, base64
from pathlib import Path

# ────────────────────────────
#  Chemins & imports dynamiques
# ────────────────────────────
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR   = SCRIPT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.extract_terms    import extract_terms_from_text
from scripts.glyph_generator  import generate_glyph
from scripts.update_dicts     import update_dict
from scripts.index_builder    import main as rebuild_index

# ────────────────────────────
#  Dictionnaire glyphes
# ────────────────────────────
DICT_PATH = ROOT_DIR / "memory" / "glyph_dict.json"
DICT_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DICT_PATH.exists():
    DICT_PATH.write_text("{}", encoding="utf-8")

# ────────────────────────────
#  Utils
# ────────────────────────────

def safe_print(line: str) -> None:
    """Imprime la ligne en ignorant les glyphes non pris en charge par CP-1252."""
    try:
        print(line)
    except UnicodeEncodeError:
        # remplace les caractères non-ASCII
        print(line.encode("ascii", "replace").decode())

# ────────────────────────────
#  Fonction principale
# ────────────────────────────

def process_file(input_path: str | Path) -> dict:
    input_path = Path(input_path)
    text       = input_path.read_text(encoding="utf-8", errors="ignore")

    # 1) Extraction de termes
    terms = extract_terms_from_text(text)
    safe_print(f"[Translator] Termes extraits : {terms}")

    # 2) Génération / mise à jour des glyphes
    mapping = {}
    for term in terms:
        glyph = generate_glyph(term)
        safe_print(f"[Translator] {term} -> {glyph}")
        update_dict(DICT_PATH, term, glyph)
        mapping[term] = glyph

    # 3) Remplacement dans le texte
    translated = text
    for term, glyph in mapping.items():
        translated = re.sub(rf"\b{re.escape(term)}\b", glyph, translated, flags=re.IGNORECASE)

    # 4) Sauvegarde du fichier traduit
    out_path = ROOT_DIR / "logs" / f"{input_path.stem}_translated.txt"
    out_path.write_text(translated, encoding="utf-8")
    safe_print(f"[Translator] Contenu glyphifié écrit dans : {out_path}")

    # 5) Compression zlib + base85
    compressed = base64.b85encode(zlib.compress(translated.encode("utf-8"))).decode("ascii")

    # 6) Mise à jour de l'index mémoire
    rebuild_index()

    return {
        "terms":            terms,
        "glyphes":          mapping,
        "translated_file":  str(out_path),
        "compression":      compressed,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        safe_print("Usage: python pipeline_traducteur.py <fichier_log.txt>")
        sys.exit(0)
    safe_print(process_file(sys.argv[1]))
