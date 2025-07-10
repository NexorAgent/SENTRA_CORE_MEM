# run_auto_translator.py
import argparse
import base64
import json
import os
import random
import re
import zlib
from collections import Counter
from datetime import datetime

parser = argparse.ArgumentParser(description="Pipeline de compression + mémoire IA/IA")
parser.add_argument(
    "-i", "--input", default="resume_translated.txt", help="Fichier source à traiter"
)
parser.add_argument(
    "--obfuscate",
    action="store_true",
    help="Randomise les glyphes pour cette exécution",
)
parser.add_argument(
    "--map-out", default=None, help="Fichier de sortie pour la table de correspondance"
)
args = parser.parse_args()

INPUT_FILE = args.input
FILENAME = os.path.splitext(os.path.basename(INPUT_FILE))[0]

DICT_PATH = "memory_zia/mem_dict.json"
ZLIB_TXT_OUTPUT = f"{FILENAME}.zlib.txt"
ZLIB_BIN_OUTPUT = f"{FILENAME}.zlib"
SRC_OUTPUT = "memory_zia/sentra_memory.zmem.src"
ZMEM_OUTPUT = "memory_zia/sentra_memory.zmem"
MAPPING_OUTPUT = args.map_out or f"{FILENAME}_mapping.json"

os.makedirs("memory_zia", exist_ok=True)

# Charger texte source
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Détection des balises dans le texte
tags = re.findall(r"<([^>]+)>", content)
tag_counts = Counter(tags)
top_tags = tag_counts.most_common(50)

if args.obfuscate:
    tag_dict = {}
    existing = set()
    for tag, _ in top_tags:
        glyph = f"§{random.randint(0,255):02X}"
        while glyph in existing:
            glyph = f"§{random.randint(0,255):02X}"
        tag_dict[tag] = glyph
        existing.add(glyph)
    with open(MAPPING_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(tag_dict, f, ensure_ascii=False, indent=2)
else:
    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            tag_dict = json.load(f)
    else:
        tag_dict = {}
    for tag, _ in top_tags:
        if tag not in tag_dict:
            new_sym = f"§{len(tag_dict):02X}"
            tag_dict[tag] = new_sym
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        json.dump(tag_dict, f, ensure_ascii=False, indent=2)

# Remplacer les balises par les symboles
compressed_content = content
for tag, sym in tag_dict.items():
    compressed_content = compressed_content.replace(f"<{tag}>", sym)

# Sauvegarde fichier compressé visible
with open(ZLIB_TXT_OUTPUT, "w", encoding="utf-8") as f:
    f.write(compressed_content)

# Compression binaire zlib
zbinary = zlib.compress(compressed_content.encode("utf-8"), level=9)
with open(ZLIB_BIN_OUTPUT, "wb") as f:
    f.write(zbinary)

# ----- Partie IA/IA : génération mémoire lisible + compressée -----
ctx_tag = datetime.now().strftime("¤SCM/%y%m%d.MEM_AUTO")
zia_memory_src = f"""@CTX:{ctx_tag}\n@DIC:{json.dumps(tag_dict, ensure_ascii=False)}\n@SEQ:\n  ¤SCM→MEM.LOC→§ZL+§DICT\n  AGENT.ZARCH→SEARCH→MEM.LOG\n  GPT↔ONLY.ON.CALL\n#\n{compressed_content}"""

with open(SRC_OUTPUT, "w", encoding="utf-8") as f:
    f.write(zia_memory_src)

compressed_ia_binary = zlib.compress(zia_memory_src.encode("utf-8"), level=9)
compressed_ia_b85 = base64.b85encode(compressed_ia_binary)

with open(ZMEM_OUTPUT, "wb") as f:
    f.write(compressed_ia_b85)

print("--- Pipeline complet exécuté ---")
print(f"Source       : {INPUT_FILE}")
print(f"ZLIB .txt    : {ZLIB_TXT_OUTPUT}")
print(f"ZLIB .bin    : {ZLIB_BIN_OUTPUT}")
print(f"ZMEM .src    : {SRC_OUTPUT}")
print(f"ZMEM .bin    : {ZMEM_OUTPUT}")
if args.obfuscate:
    print(f"Mapping      : {MAPPING_OUTPUT}")
