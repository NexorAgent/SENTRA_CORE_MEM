#!/usr/bin/env python3
"""actions_dashboard.py -- Résumé simple des actions.

Lire `logs/actions.log` et produire `logs/actions_report.md` avec le
nombre d'occurrences par type d'action.

Usage manuel :
    python -m scripts.actions_dashboard
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "actions.log"
REPORT_FILE = PROJECT_ROOT / "logs" / "actions_report.md"

# Capture "] action ->" ou "] action -" ou "] action:" etc.
ACTION_REGEX = re.compile(r"\] *([^->:]+?)(?:->|-|:)" )

def parse_actions() -> Counter:
    """Retourne un compteur {action: occurrences}."""
    counts: Counter[str] = Counter()
    if not LOG_FILE.exists():
        return counts
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = ACTION_REGEX.search(line)
            if match:
                action = match.group(1).strip()
            else:
                parts = line.split()
                action = parts[1] if len(parts) > 1 else "UNKNOWN"
            counts[action] += 1
    return counts


def generate_report() -> Path:
    counts = parse_actions()
    lines = [
        f"# Tableau de bord des actions – {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"Total détecté : {sum(counts.values())}",
        "",
    ]
    for action, count in counts.most_common():
        lines.append(f"- **{action}** : {count}")
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_FILE


def run() -> dict:
    path = generate_report()
    return {"réponse": f"📊 Rapport d'actions généré : {path}"}


if __name__ == "__main__":
    report = generate_report()
    print(f"📊 Rapport écrit dans {report}")
