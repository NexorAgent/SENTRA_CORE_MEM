# SENTRA CORE MEM – Architecture 2025

## Objectifs
- Mémoire persistante structurée sous PostgreSQL + extension pgvector.
- Couche FastAPI unique conservant les routes historiques et exposée via MCP.
- Embeddings locaux (SentenceTransformers) avec fallback déterministe hors GPU.
- Déploiement prêt pour VPS OVH Debian (Docker Compose, Postgres, healthchecks).

## Modules clé
| Module | Rôle |
|--------|------|
| `app/core/config.py` | Configuration centralisée (`pydantic-settings`) |
| `app/db/` | Base SQLAlchemy, moteur, types hybrides pgvector |
| `app/memory/` | Repository + service mémoire Postgres |
| `app/vector/` | Service d embeddings (load + fallback) |
| `app/routes/` | Endpoints (files, memory, rag, google, bus, git, n8n, zep) |
| `sentra_mcp_gateway/` | Passerelle FastAPI -> MCP |
- `sentra_mcp_gateway` expose egalement un outil `sentra.echo` pour verifier rapidement la connectivite MCP depuis un GPT custom.
| `docker-compose.yml` | Stack (api, postgres, mcp, n8n, filebrowser, worker) |

## Stockage & recherche
```
+---------------------------+
| PostgreSQL (pgvector)     |
|  memory_notes             |
|    - note_id, user, tags  |
|    - payload JSON         |
|    - embedding vector     |
|  rag_documents            |
|    - collection/doc_id    |
|    - payload JSON         |
|    - embedding vector     |
+---------------------------+
          ^         |
          |         v
+---------------------------+
| EmbeddingService         |
|  - SentenceTransformer   |
|  - fallback SHA256       |
+---------------------------+
          ^         |
          |         v
+---------------------------+
| MemoryRepository / RAG   |
|  - CRUD + archives       |
|  - Similarité cosine     |
|  - Filtres tags hybrides |
+---------------------------+
```

## Flux principaux
1. **Ajout mémoire** (`POST /memory/note/add`)
   - Audit -> validation -> `MemoryService.add_note()`
   - Insert Postgres + embedding + archive gzip (`memory/library/archives/<id>.zmem`).
2. **Recherche mémoire** (`POST /memory/note/find`)
   - Texte + tags -> cosine (pgvector) ou fallback Python -> DTO (score, tags, metadata).
3. **RAG** (`/rag/index` & `/rag/query`)
   - Collections en base (`rag_documents`) réutilisant le même moteur d embeddings.
4. **Connecteurs**
   - Google APIs (service account), bus slim Google Sheets + n8n, gestion GitOps, déclencheur n8n.

## Observabilité & sécurité
- Audit NDJSON (`logs/audit.log`).
- Healthchecks : `/health`, `/mcp/healthz`, `pg_isready`.
- Auth Google via service account, bus sécurisé par idempotency keys.
- Pare-feu UFW + reverse proxy recommandé (Caddy/Traefik/NGINX).

## Déploiement (résumé)
1. Installer Docker/Docker Compose, Postgres (ou utiliser `docker compose`).
2. Cloner le dépôt dans `/opt/sentra`.
3. Configurer `.env` (URL base, webhooks, credentials).
4. `docker compose up -d --build`.
5. Vérifier les services (`docker compose ps`, `curl http://localhost:8000/health`).
6. Option : service systemd pour automatiser (`docs/ovh_debian_manual.md`).

## Opérations
- **Tests** : `python -m pytest`.
- **Mises à jour** : `git pull && docker compose up -d --build`.
- **Sauvegardes** : `pg_dump` + synchronisation des archives `.zmem`.
- **Restauration** : restaurer dump Postgres puis recharger les archives si nécessaire.

## Roadmap interne
- Ajout migrations Alembic & intégration CI.
- Observabilité Prometheus/Loki.
- Gestion de jobs vectoriels avancés (profil `vector-worker`).

Pour les étapes détaillées d installation : `README.md` + `docs/ovh_debian_manual.md`.


| pp/routes/mcp_bridge.py | Bridge HTTP vers MCP (init + call tools)
