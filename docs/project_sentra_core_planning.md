# 📋 PLAN DE PROJET – SENTRA_CORE_MEM

**Nom IA :** SENTRA CORE  
**Version actuelle :** v0.2 – 25/05/2025  
**Objectif global :** IA autonome, structurée, compressée, interopérable avec Discord/Notion/Git.

---

## ✅ ÉTAPES VALIDÉES

### 1. STRUCTURE TECHNIQUE
- [x] Création de `SENTRA_CORE_MEM_v0.1`
- [x] Arborescence : `/memory`, `/scripts`, `/sentra`, `/reports`, `/logs`, `/docs`
- [x] Fichiers système :  
  - `sentra_memory.json`  
  - `glyph_rules.txt`  
  - `SENTRA_OATH.md`  
  - `config.py`, `sentra_config.py`

---

### 2. MÉMOIRE COMPRESSÉE + LOGS
- [x] Compression glyphique fonctionnelle (`memory_manager.py`)
- [x] Journal d’exécution `execution_log.txt` (append-only)
- [x] Mécanisme multi-agent débuté

---

### 3. GÉNÉRATION DE RAPPORT MARKDOWN
- [x] `markdown_generator.py` prêt à l’emploi
- [x] Structure de fichiers `reports/YYYY/MM/DATE_slug.md`
- [x] Contenu Markdown : mémoire + logs
- [x] Intégration dans cycle automatisé

---

### 4. ORCHESTRATION & AGENTS
- [x] `orchestrator.py` (dispatcher / router)
- [x] Appel dynamique `call_agent(name)`
- [x] Fallback standard : "Aucun agent reconnu…"

---

### 5. CYCLES DE SCRIPT AUTOMATISÉS
- [x] `sentra_cycle.bat` : orchestrateur + mémoire + rapport + Git push dev
- [x] `merge_to_main.bat` : fusion propre `dev → main`

---

### 6. INTÉGRATION NOTION
- [x] Agent `agent_notion.py` actif
- [x] Envoi vers base Notion testée avec token + DB ID
- [x] Lecture / synchronisation stabilisée

---

### 7. BOT DISCORD
- [x] Création bot Discord `SENTRA CORE`
- [x] Ajout au serveur via lien avec scopes :
  - `bot`, `applications.commands`
- [x] Permissions OK :  
  - Send Message, Read History, Use Slash Commands
- [x] Slash commands opérationnelles :  
  - `/report` (envoie Markdown généré)  
- [x] Rapport généré dans Discord : 🧠 mémoire + logs

---

## 🔄 EN COURS

### 8. MAPPING DES INTENTIONS
- [ ] `/sync` retourne "aucun agent reconnu"
- [ ] À corriger : dispatcher `"synchronisation mémoire"` → `call_agent("notion")`

---

## 🔜 À VENIR

### 9. DISCORD VOCAL
- [ ] Lecture canal vocal
- [ ] STT automatique (ex. Whisper, OpenAI, Deepgram)
- [ ] Transcription en mémoire / log

---

### 10. STRUCTURE DE MÉMOIRE HIÉRARCHISÉE
- [ ] Niveau 1 : local (JSON)
- [ ] Niveau 2 : Notion
- [ ] Niveau 3 : distant (API / DB vectorielle)
- [ ] Compression glyphique multi-niveau

---

### 11. EXPORTATION GIT VERSIONNÉE
- [ ] Auto-push vers `dev`, `main`, `logs`
- [ ] Dossier `/reports` dans branche dédiée

---

### 12. MULTI-MODULES GPT INTELLIGENTS
- [ ] `ZCODEX` → Créateur de prompts personnalisés  
- [ ] `ZREZO` → Scraper & veille réseau  
- [ ] `ZARCH` → Mémoire interne indexée  
- [ ] `ZCHALL` → Simulation de prompts/action en sandbox  
- [ ] `ZFORGE` → Création de clones GPT spécialisés

---

📦 _Dernière mise à jour : 25/05/2025 - validé par Julien / SENTRA CORE_

## SENTRA\_CORE\_MEM – PLAN OPÉRATIONNEL v0.4 (27/05/2025)

### OBJECTIF GÉNÉRAL

Création d'une IA personnelle autonome, structurée, avec mémoire persistante, agents spécialisés et **compression glyphique automatique** pour réduire drastiquement le coût OpenAI.

---

### ARCHITECTURE TECHNIQUE (rappel)

* Dossiers : `/memory`, `/scripts`, `/sentra`, `/reports`, `/logs`, `/docs`
* Fichiers système : `sentra_memory.json`, `glyph_rules.txt`, `SENTRA_OATH.md`, `config.py`
* Compression glyphique **niveau 1** déjà active ➜ v0.3

---

## PHASES OPÉRATIONNELLES

*(les deadlines sont exprimées en J+n à partir du 27/05/2025)*

| Phase            | Tâche                         | Description                                                                 | Deadline                  |
| ---------------- | ----------------------------- | --------------------------------------------------------------------------- | ------------------------- |
| **A**            | dispatcher + /sync            | Corriger mapping "synchronisation mémoire" → agent Notion                   | J‑1 ✔️                    |
|                  | multi‑agent dispatcher        | Reconnaissance d'intention auto (rapport, sync…)                            | J‑2 ✔️                    |
| **B**            | ZARCH                         | Lecture/recherche logs & mémoire compressée                                 | J‑4                       |
|                  | glyph\_v2                     | **Compression glyphique IA⇄IA + indexation**                                | J‑5 ✔️ (implémentée v0.3) |
|                  | ZMEM\_VIEWER                  | Vue mémoire Notion lisible avec filtre                                      | J‑7                       |
| **C**            | ZSYNC\_SCHEDULER.py           | Lancer auto des sync mémoire + logs                                         | J‑6                       |
|                  | ZSUMMARY                      | Résumé automatique des logs quotidiens                                      | J‑8                       |
| **D**            | CHANGELOG.md                  | Suivi versions et modifs agent/mémoire                                      | J‑1 ✔️                    |
|                  | NOTICE.md                     | Mode d'emploi complet du système                                            | J‑3                       |
|                  | reports/YYYY/MM/slug.md       | Génération automatisée cycle + log                                          | J‑3                       |
| **E – NOUVELLE** | **Auto‑Traducteur glyphique** | Implémenter `auto_translator.py` : tables statiques + règles + fallback GPT | **J‑2**                   |
|                  | glyph\_codec.py               | Fonctions `to_glyph()` / `from_glyph()` + zlib/base85                       | J‑2                       |
|                  | migrate\_memory.py            | Script de migration des mémoires existantes vers N3‑Plus                    | J‑3                       |
|                  | Intégration agents            | Petit : smalltalk, notion, forge → compression automatique                  | J‑4                       |
|                  | Rapports                      | Décodage à la volée dans `/report`                                          | J‑4                       |
|                  | z.bench\_ratio                | Commande Discord : affiche gain (%) moyen                                   | J‑5                       |

---

### OBJECTIFS 30 JOURS (mise à jour)

* IA personnelle **avec compression glyphique automatique** (N3‑Plus) fonctionnelle.
* Coût OpenAI réduit ≥ 80 % / requête.
* Logs & mémoire compressés + indexables (ZARCH).
* Agents spécialisés utilisables via `/sync`, `/report`, `/chat`.
* Synchronisation automatique (scheduler local).
* Hébergement facultatif (local ou Render gratuit si besoin).

---

### NON PRIORITAIRE (inchangé)

* Pas de SaaS / commercialisation.
* Pas de pipeline vocal (reporté après phase mémoire avancée).
* Pas de système de paiement externe.

---

*Màj : 27/05/2025 — Laurent (SENTRA CORE)*

| Étape                     | Description                                                | Deadline | Statut         |
| ------------------------- | ---------------------------------------------------------- | -------- | -------------- |
| Fichier BAT pipeline      | Automatisation batch glyphique                             | ASAP     | ✅ (prêt)       |
| MAJ Manuel utilisateur    | Ajout doc, tuto glyphique, batch, Discord                  | ASAP     | 🟡 (à faire)   |
| Opti prompt Devstral      | Tests, feedbacks, tuning température, indexation glyphique | +1j      | 🔄 (démarrage) |
| Expérimentations Devstral | Usage condenseur, spécialisation logs, nouveaux agents     | +2j      | ⏳ (en plan)    |
| Discord Slash Command     | Activation pipeline via Discord (Open API)                 | +3j      | ⏳ (à créer)    |
| Planification v0.4        | Validation, passage cycle complet, déploiement             | +4j      | ⏳ (à suivre)   |
