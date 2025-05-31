# scripts/glyph_generator.py

def generate_glyph(term: str) -> str:
    glyph_map = {
        "mémoire": "🧠",
        "synchronisation": "⟁",
        "orchestration": "⛓️",
        "agent": "🧩",
        "rapport": "📄",
        "compression": "📦",
        "markdown": "📝",
        "glyphique": "🪄",
        "version": "🔢",
        "installation": "⚙️",
        "demande": "❓",
        "openai": "🤖",
        "interface": "🧭",
        "résumé": "🧾",
        "code": "💻",
        "notion": "🔗",
        "journal": "📚"
    }
    # Retourne un glyphe connu ou un glyphe générique construit à partir des premières lettres
    return glyph_map.get(term.lower(), f"<{term[:3].upper()}>")
