def detect_intent_and_route(message: str) -> dict:
    msg_lower = message.lower()

    # Intent de sauvegarde/ajout en mémoire
    if any(kw in msg_lower for kw in ["sauvegarde", "mémoire", "note", "enregistre", "garde cette idée", "rappelle", "mémo"]):
        return {
            "intent": "save_note",
            "réponse": "🧠 Note reconnue et transmise au module mémoire.",
            "glyph": "💾"
        }

    # Intent chat/interrogation
    elif "?" in message or any(message.lower().startswith(p) for p in ["que ", "qui ", "où ", "comment ", "pourquoi ", "quand "]):
        return {
            "intent": "chat",
            "réponse": f"Vous m’avez posé : « {message} »",
            "glyph": "ℹ️"
        }

    # Intent génération de rapport Markdown
    elif any(kw in msg_lower for kw in ["markdown", "document", "rapport"]):
        return {
            "intent": "markdown_gen",
            "réponse": "📄 Génération de markdown déclenchée.",
            "glyph": "📝"
        }

    # Sinon, intention inconnue
    else:
        return {
            "intent": "unknown",
            "réponse": f"Message reçu : « {message} »",
            "glyph": "❓"
        }
