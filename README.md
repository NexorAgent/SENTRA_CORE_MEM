# SENTRA_CORE_MEM – Orchestrateur IA modulaire

## Vision globale
Bâtir une couche d’orchestration disciplinée et modulaire (SENTRA_CORE_MEM) qui tourne sur un VPS et peut :
- Gérer une mémoire persistante hybride (cœur VPS, sauvegarde Google Drive, futur store vectoriel Zep).
- Piloter des workflows n8n (Google, Notion, Discord, Telegram, WhatsApp, …).
- Fournir un assistant personnel multi‑fonctions (prise de notes, création de fichiers, déclenchement d’actions).
- Faire respecter une charte IA stricte pour garantir cohérence et traçabilité.
- Évoluer vers un orchestrateur MCP externe lorsque les APIs classiques disparaîtront.

---

## Organisation des fichiers
- Chaque fichier possède un emplacement canonique (logique « bibliothèque »).
- Création au langage naturel : « Crée `projects/2025/notes/brief.md`. »
- Lecture/recherche par chemin explicite : « Lis `projects/2025/notes/brief.md`. »
- Markdown privilégié pour l’homogénéité.
- Les logs ou artefacts temporaires restent hors de l’arbre mémoire principal.

---

## Règles de conduite IA
- La charte IA est relue avant chaque interaction.
- Toutes les 30 interactions :
  - Persistance du fil courant dans `/memory/` et sur Drive.
  - Relecture automatique du contexte pour limiter la dérive.
- RBAC et journalisation NDJSON restent actifs en permanence.

---

## Connecteurs
- Google Sheets (bus « slim », communication bidirectionnelle).
- Google Drive (stockage documentaire).
- Google Calendar (évènements).
- Webhooks/automatisations n8n.
- À venir : Discord, Telegram, WhatsApp, Notion, Revit API.

---

## Options de mémoire persistante
| Option | Avantage | Limite |
|--------|----------|--------|
| Zep / store vectoriel externe | Indexation native | Dépendance SaaS |
| Google Drive (brut) | Capacité, redondance | Tri/recherche manuels |
| Mémoire locale VPS | Contrôle total, rapidité | Nécessite indexation (Chroma/FAISS) |

Approche hybride recommandée : VPS pour l’opérationnel, Drive pour la sauvegarde, Zep pour l’échelle.

---

## GPT & MCP
- ChatGPT (mode développeur) joue le rôle d’orchestrateur quotidien.
- GPT consigne des notes, crée des fichiers et déclenche des workflows n8n.
- La couche MCP permettra d’orchestrer Notion, Google, Revit via la même logique.

---

## Agent professeur personnel
- Agent pédagogique dédié avec référentiel de cours.
- Capable de bâtir des programmes longs, suivre la progression, générer tests et cas pratiques.
- Mémoire pédagogique isolée dans `/memory/courses/`.

---

## Sécurité & discipline
- RBAC strict (owner / writer / reader / system).
- Journal NDJSON en continu.
- Sauvegardes Drive et rotation des logs.
- Tunnel Cloudflare + pare-feu actif.

---

## Feuille de route par phases
| Phase | Statut | Points clés |
|-------|--------|-------------|
| 1 – Fondations | terminé | Docker Compose (API, n8n, orchestrator, Discord, Filebrowser), endpoints FastAPI (`files`, `memory`, `bus`, `google`), GitOps + sauvegardes, durcissement réseau |
| 2 – Connecteurs | en cours | Google Drive/Sheets/Calendar, workflows n8n, intégrations Discord/Telegram |
| 3 – Mémoire locale | planifié | Indexation ChromaDB, sauvegardes Drive/HDD, organisation « bibliothèque » |
| 4 – Règles IA & contrat API | planifié | Charte à chaque échange, mémoire toutes les 30 interactions, réponses bus « slim », relais Idempotency n8n, RAG `results` + `source`, écriture fichiers en texte |
| 5 – Assistant personnel | à venir | GPT Dev Mode + MCP, prise de notes (WhatsApp voix → texte), professeur personnel |
| 6 – Orchestration avancée | futur | MCP externe (Notion, Revit…), agents spécialisés (veille, SEO, BIM, automation), gouvernance IA évolutive |

---

## Tests
La suite Pytest couvre `files`, `memory`, `bus`, `google`, `rag` ainsi qu’un scénario bout‑en‑bout.
```bash
python -m pytest -q
python -m pytest -k bus
```

---

## Instantané Phase 4 – Endpoints

### Bus (contrat « slim »)
```http
POST /bus/send
{
  "user": "ops",
  "agent": "dispatcher",
  "payload": {"ping": 1},
  "metadata": {"spreadsheet_id": "sheet-1", "worksheet": "Requests"},
  "idempotency_key": "ping-1"
}
⇒ {"message_id": "…", "status": "pending", "timestamp": "…"}
```
`/bus/poll` et `/bus/updateStatus` consomment la même `metadata` pour cibler la feuille.

### Déclencheur n8n
```http
POST /n8n/trigger
{
  "user": "ops",
  "agent": "dispatcher",
  "payload": {"action": "sync"},
  "idempotency_key": "sync-1"
}
```
L’en‑tête `Idempotency-Key` est relayé uniquement si fourni.

### RAG
- `/rag/index` génère des IDs depuis texte + metadata (ou respecte `doc_id`).
- `/rag/query` renvoie `results` et filtre les items sans `source`.

### Files
`files.write` accepte un champ `content` texte ; `idempotency_key` reste optionnel.

---

## Mise en route rapide
1. `git clone https://github.com/NexorAgent/SENTRA_CORE_MEM.git`
2. Copier `.env.example` en `.env` et renseigner `API_HOST_PORT`, `N8N_WEBHOOK_URL`, `BASE_DIR`, `SANDBOX_DIR`, `GOOGLE_CREDENTIALS_FILE`, …
3. Démarrer l’API (Docker Compose ou `uvicorn app.main:app`).
4. Lancer un smoke test : `curl -sS -H "X-ROLE: writer" … /bus/send`.

---

## Notes
Ce README remplace l’ancienne documentation (DeepSeek / Phase 0) et reflète la roadmap Phase 4.

---

MIT License (c) 2025 SENTRA_CORE_MEM.
