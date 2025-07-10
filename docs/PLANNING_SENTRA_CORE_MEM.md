# 📅 PLANNING GLOBAL – SENTRA_CORE_MEM

**Dernière mise à jour : 2025-05-29 07:59**

---

## PHASE 1 – FONDATIONS TECHNIQUES

| Étape | Tâche | Statut | Objectif |
|-------|-------|--------|----------|
1.1 | Structuration des dossiers | ✅ Terminé | `/memory`, `/scripts`, `/sentra`, `/logs`, `/reports`, `/docs` |
1.2 | Orchestrateur `orchestrator.py` + dispatcher | ✅ Terminé | Centralise les intentions → agents |
1.3 | Agents de base (notion, smalltalk, markdown) | ✅ Terminé | Exécution modulaire |
1.4 | Script .bat `sentra_cycle.bat` | ⚙️ OK | Lancer orchestrateur + agent |

---

## PHASE 2 – MODULE GLYPHIQUE

| Étape | Tâche | Statut | Objectif |
|-------|-------|--------|----------|
2.1 | `extract_terms.py` → extraction de termes | ✅ OK | Isoler mots-clés pertinents |
2.2 | `glyph_generator.py` / `GLYPH_FORGER.py` | ⚠️ Partiel | Génération glyphes visuels et abréviations |
2.3 | `update_dicts.py` | ✅ OK | Mise à jour automatique des dictionnaires |
2.4 | `pipeline_traducteur.py` | ✅ OPÉRATIONNEL | Traduction glyphique + compression |
2.5 | `run_auto_translator.py` | ⚠️ À stabiliser | Lance une traduction autonome via .bat |
2.6 | Niveau 3 compression (`glyph_rules.txt`) | 🔜 À intégrer | Codification glyphique avancée |
2.7 | Gestion dictionnaire + audit glyphes | 🔜 | Règles unicité, validité UTF8 |

---

## PHASE 3 – INTÉGRATION MÉMOIRE

| Étape | Tâche | Statut | Objectif |
|-------|-------|--------|----------|
3.1 | `sentra_memory.json` fonctionnel | ✅ OK | Stockage brute compressée |
3.2 | Compression/décompression locale | ✅ OK | Logs + textes compressés |
3.3 | Intégration Notion | ⚠️ À synchroniser | Export mémoire niveau 2 |
3.4 | Visualisation filtrée Notion | 🔜 | Recherche + tags |
3.5 | `ZSYNC_SCHEDULER.py` | 🔜 | Lancer auto sync mémoire/log |

---

## PHASE 4 – INTERFACE DISCORD

| Étape | Tâche | Statut | Objectif |
|-------|-------|--------|----------|
4.1 | Bot Discord `SENTRA_CORE` actif | ✅ OK | Slash commands opérationnelles |
4.2 | `/report`, `/sync` | ⚠️ `/sync` à corriger | Intégration agent |
4.3 | Ajout vocal (STT) | 🔜 | Transcription vocale → mémoire |
4.4 | Notifications résultats | 🔜 | Messages Discord compressés |

---

## PHASE 5 – MODULES Z-INTELLIGENTS

| Module | Fonction | Priorité |
|--------|----------|----------|
ZCODEX | Générateur prompts intelligents | 🔜 |
ZREZO | Recherche réseaux & scraping | 🔜 |
ZARCH | Consultation mémoire compressée | ⚠️ Prochaine cible |
ZCHALL | Test sandbox IA | 🕒 |
ZFORGE | Créateur d'agents | 🕒 |

---

## PHASE 6 – PASSERELLE GPT → MÉMOIRE

| Étape | Tâche | Objectif |
|-------|------|----------|
6.1 | Lecture mémoire compressée | ⚠️ CENTRAL | Accès direct GPT |
6.2 | Injection mémoire à la demande | ✅ En test | GPT utilise le contexte mémoire |
6.3 | Règles d'écriture mémoire | 🔜 | ZIA auto-injection contrôlée |
6.4 | Filtrage intelligent mémoire | 🔜 | GPT lit que le pertinent |

---

## PHASE 7 – DOCUMENTATION

| Étape | Tâche | Objectif |
|-------|------|----------|
7.1 | `CHANGELOG.md`, `NOTICE.md` | ✅ / ⚠️ | Historique + manuel |
7.2 | `glyph_rules.txt` | 🔜 | Codification visuelle standard |
7.3 | Git auto-push | 🔜 | Dev, main, logs, reports |

---

## PHASE 8 – VISION LONG TERME

| Axe | Possibilité | Statut |
|-----|-------------|--------|
AGI locale | Injection DTU, CCTP, normes | 🧠 |
Commercialisation | Si système stable | 💼 |
Interface CLI/web | Simplification usage | 🖥️ |
Interaction audio IA | Assistant vocal connecté | 🗣️ |

