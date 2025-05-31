import sys
import os
import json
import zlib
import base64

if len(sys.argv) < 2:
    print("Usage: python zmem_loader.py <nom_memoire>")
    sys.exit(1)

name = sys.argv[1]
zmem_path = os.path.join("memories", f"{name}.zmem")

if not os.path.exists(zmem_path):
    print(f"ERREUR : La mémoire '{name}' n'existe pas dans le dossier 'memories'.")
    sys.exit(1)

# Lecture + décompression
with open(zmem_path, "rb") as f:
    encoded = f.read()
decoded_bytes = base64.b85decode(encoded)
decoded = zlib.decompress(decoded_bytes).decode("utf-8", errors="ignore")

# Suppression du BOM Unicode si présent
if decoded.startswith("\ufeff"):
    decoded = decoded.lstrip("\ufeff")

print("====== MÉMOIRE DÉCODÉE ======")
print(decoded)
