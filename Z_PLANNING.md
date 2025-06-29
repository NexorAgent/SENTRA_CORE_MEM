# Planning opérationnel SENTRA_CORE_MEM

Basé sur `docs/project_sentra_core_planning.md` (mise à jour 27/05/2025).

## Phases clés

- **A** : `dispatcher` + `/sync` (J‑1 à J‑2)
  - Correction du mapping vers l'agent Notion
  - Dispatcher multi‑agent
- **B** : `ZARCH`, `glyph_v2`, `ZMEM_VIEWER` (J‑4 à J‑7)
- **C** : `ZSYNC_SCHEDULER.py` (J‑6) et `ZSUMMARY` (J‑8)
- **D** : documentation (`CHANGELOG.md`, `NOTICE.md`, rapports cycliques)
- **E – Nouvelle** : traducteur glyphique et outils (`glyph_codec.py`, `migrate_memory.py`)

## Objectifs 30 jours

- IA personnelle avec compression glyphique N3‑Plus
- Coût OpenAI réduit ≥ 80 % par requête
- Logs & mémoire compressés et indexables
- Agents `/sync`, `/report`, `/chat`
- Scheduler local optionnel

_Màj : 27/05/2025_
