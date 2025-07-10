# Z\_PLANNING.md

**SENTRA\_CORE\_MEM – Phase « Autogestion complète »**
*Timeframe : 09 Jun 2025 → 06 Jul 2025 (4 weekly sprints)*

---

## Sprint timeline

| Symbolic Tag                         | Sprint Window        | Focus                                    | Key Deliverables                                                                  |
| ------------------------------------ | -------------------- | ---------------------------------------- | --------------------------------------------------------------------------------- |
| 🔰 **SPRINT\_0::CADRAGE**            | 09 Jun 2025          | Cadrage & pré‑requis                     | Plan validé, issues GitHub créées, repo congelé                                   |
| 🏁 **SPRINT\_1::GITOPS\_MEM**        | 09 Jun – 15 Jun 2025 | GitOps & mémoire par branche             | `SENTRA_GITOPS.py` v0.1, cycle unifié v1, `mem_dev.json` / `mem_main.json`        |
| 🛠️ **SPRINT\_2::AUTOMATION\_REGEN** | 16 Jun – 22 Jun 2025 | Automatisation & régénération adaptative | `SENTRA_GITOPS.py` v0.2, `SENTRA_REGEN_CORE` v0.1, injection auto `Z_MEMORIAL.md` |
| 🤝 **SPRINT\_3::CLONES\_COLLAB**     | 23 Jun – 29 Jun 2025 | Collaboration IA/IA & clones             | Glyphique N2 stable, `SENTRA_MULTICLONE` v0.1, canal dialogue IA/IA               |
| 🛡️ **SPRINT\_4::CYCLE\_AUTONOME**   | 30 Jun – 06 Jul 2025 | Cycle autonome & audit                   | `ZSYNC_SCHEDULER.py` v1, audit automatique, docs mises à jour                     |

---

## Detailed Workplan

### 🔰 SPRINT\_0::CADRAGE (09 Jun 2025)

* Validate roadmap and planning.
* Freeze repository structure (`main`, `dev`).
* Create GitHub issue **“Phase Autogestion IA”** with sub‑tasks for each sprint.
* Generate **Z\_PLANNING.md** (this file).
* Tag log in `Z_MEMORIAL.md`: `2025-06-09 – 🔰 SPRINT_0::CADRAGE – Cadrage initial terminé.`

### 🏁 SPRINT\_1::GITOPS\_MEM (09 Jun – 15 Jun 2025)

* Deliver **`SENTRA_GITOPS.py` v0.1** (CLI status/add/commit/push).
* Refactor `sentra_cycle.bat` to include session summary, auto‑commit, sync.
* Implement branch‑aware memory (`mem_dev.json`, `mem_main.json`).
* Store weekly review: `/reports/2025/06/review_sprint_1.md`.

### 🛠️ SPRINT\_2::AUTOMATION\_REGEN (16 Jun – 22 Jun 2025)

* Extend `SENTRA_GITOPS.py` with smart branching & merge.
* Deploy `SENTRA_REGEN_CORE` with adaptive prompt/glyph update.
* Auto‑inject `Z_MEMORIAL.md` each cycle.
* Weekly review path: `/reports/2025/06/review_sprint_2.md`.

### 🤝 SPRINT\_3::CLONES\_COLLAB (23 Jun – 29 Jun 2025)

* Finalise glyphique N2 spec (`/docs/glyph_schema_v2.md`).
* Release `SENTRA_MULTICLONE v0.1`.
* Implement IA/IA dialogue wrapper.
* Weekly review path: `/reports/2025/06/review_sprint_3.md`.

### 🛡️ SPRINT\_4::CYCLE\_AUTONOME (30 Jun – 06 Jul 2025)

* Launch `ZSYNC_SCHEDULER.py` and auto‑audit.
* Update documentation & diagrams.
* Weekly review path: `/reports/2025/06/review_sprint_4.md`.

---

## KPI Dashboard

| Metric                 | Target  | Measure Source         |
| ---------------------- | ------- | ---------------------- |
| Cycle success rate     | ≥ 90 %  | scheduler logs         |
| Cycle latency          | ≤ 2 min | scheduler stats        |
| Memory/branch coverage | 100 %   | validation hook        |
| Manual merges          | → 0     | GitHub PR stats        |
| Audit alerts resolved  | < 24 h  | Discord #sentra-alerts |

---

*Last updated: 09 Jun 2025*
*Owner: **SENTRA\_CENTRAL***
