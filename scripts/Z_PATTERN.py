# Analyse les logs pour détecter les mots candidats à glyphisation
import re
from collections import Counter

def detect_terms(texts: list[str], min_occurrence=2) -> list[str]:
    words = [w for t in texts for w in re.findall(r"\b[\wÀ-ÿ]{4,}\b", t.lower())]
    return [w for w, c in Counter(words).items() if c >= min_occurrence]