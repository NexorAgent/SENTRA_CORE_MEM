import re

def extract_terms_from_text(text: str) -> list[str]:
    """
    Extrait les termes techniques/mots-clés d'un texte.
    • mots de 6 lettres et plus
    • chaînes en MAJUSCULES
    • vocabulaire métier prédéfini
    """
    # Mots ≥ 6 lettres
    mots = set(re.findall(r"\b([A-Za-zÀ-ÖØ-öø-ÿ]{6,})\b", text))

    # Liste de mots métier à compléter librement
    lexique_metier = {
        "orchestrateur", "synchronisation", "glyphique", "pipeline",
        "mémoire", "agent", "rapport", "markdown"
    }
    mots.update({mot for mot in text.split() if mot.lower() in lexique_metier})

    return list(mots)
