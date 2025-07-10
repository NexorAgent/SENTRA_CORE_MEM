
import json, re
from pathlib import Path

# Chemin absolu par défaut vers la mémoire JSON
MEM_DEFAULT = str(Path(__file__).resolve().parent.parent / "memory" / "sentra_memory.json")

def glyph_v1_decode(text: str) -> str:
    """Stub : renvoie tel quel."""
    return text

def load_memory(path: str = MEM_DEFAULT):
    entries = []
    if not Path(path).exists():
        return entries
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries = data
    except json.JSONDecodeError:
        pass
    return entries

# Remplace complètement regex_search par :
def regex_search(data, pattern: str):
    """Recherche insensible à la casse (simple substring)."""
    p = pattern.lower()
    hits = []
    for i, entry in enumerate(data):
        txt = (entry.get("text")
               or entry.get("content")
               or entry.get("contenu")
               or "").lower()
        if p in txt:
            hits.append((i, entry))
    return hits

def quick_query(query: str, depth: int = 1,
                mem_path: str = MEM_DEFAULT, limit: int = 5) -> list[str]:
    """Retourne des blocs markdown contexte pour Discord."""
    entries = load_memory(mem_path)
    hits = regex_search(entries, query)[:limit]
    blocs = []
    for idx, (i, _) in enumerate(hits, 1):
        start = max(0, i - depth)
        end   = min(len(entries), i + depth + 1)
        ctx_lines = [
            f"- {glyph_v1_decode(e.get('text') or e.get('content') or e.get('contenu') or '')}"
            for e in entries[start:end]
        ]
        blocs.append(f"**Contexte {idx}/{len(hits)}**\n" + "\n".join(ctx_lines))
    return blocs

# CLI simple
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--depth", type=int, default=1)
    args = p.parse_args()
    blocs = quick_query(args.query, depth=args.depth)
    print("\n\n".join(blocs) if blocs else "🔍 Rien trouvé.")
