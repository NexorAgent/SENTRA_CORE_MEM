import time
from pathlib import Path
from Z_PATTERN import detect_terms
from GLYPH_FORGER import forge_glyph

LOG_DIR = Path("logs")
MEM_PATH = Path("memory") / "glyph_watch.log"

if __name__ == "__main__":
    print("[Z-WATCH] Surveillance des logs active…")
    seen = set()
    while True:
        all_txt = []
        for file in LOG_DIR.glob("*.txt"):
            content = file.read_text(encoding="utf-8", errors="ignore")
            all_txt.append(content)
        terms = detect_terms(all_txt, min_occurrence=3)
        for t in terms:
            if t not in seen:
                g = forge_glyph(t)
                MEM_PATH.parent.mkdir(exist_ok=True, parents=True)
                with MEM_PATH.open("a", encoding="utf-8") as f:
                    f.write(f"{t} → {g}\n")
                seen.add(t)
        time.sleep(30)  # toutes les 30s
