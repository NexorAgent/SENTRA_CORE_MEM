import os
import shutil
from datetime import datetime

# Utiliser le chemin du fichier comme référence racine
ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "../archive")
os.makedirs(TARGET, exist_ok=True)

EXCLUDE = [".git", "__pycache__", "memories", "archive", "logs", ".DS_Store"]

def should_ignore(path):
    return any(part in EXCLUDE for part in path.split(os.sep))

def copy_filtered(src, dst):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        if should_ignore(rel_path):
            continue
        dest_root = os.path.join(dst, rel_path)
        os.makedirs(dest_root, exist_ok=True)
        for file in files:
            fsrc = os.path.join(root, file)
            fdst = os.path.join(dest_root, file)
            if not should_ignore(fsrc):
                shutil.copy2(fsrc, fdst)

if __name__ == "__main__":
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(TARGET, f"archive_{stamp}")
    os.makedirs(dest, exist_ok=True)
    copy_filtered(os.path.join(ROOT, ".."), dest)
    print(f"📦 Archive créée : {dest}")
