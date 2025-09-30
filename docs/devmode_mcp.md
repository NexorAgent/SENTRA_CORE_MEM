# Intégration MCP – ChatGPT Developer Mode

## 1. Lancer les services Docker

```bash
docker compose up -d api mcp
```

Le sidecar MCP écoute sur le port `8400` dans le réseau Docker. Pour un accès local (ChatGPT Dev Mode), publiez le port :

```bash
docker compose up -d --build mcp
# exposez 8400:8400 dans votre override local si besoin
```

## 2. Ajouter le serveur MCP dans ChatGPT Dev Mode

1. Ouvrir ChatGPT → Settings → Developer Mode → Servers → Add server.
2. Nom : `sentra-mcp`
3. URL : `http://localhost:8400`
4. Aucun secret requis.

## 3. Tools disponibles

| Tool | Description | Rôle | Payload principal |
|------|-------------|------|-------------------|
| `files.read` | Lire un fichier autorisé | reader | `{user, path}` |
| `files.write` | Écrire/committer un fichier | writer | `{user, agent, path, content, idempotency_key?}` |
| `doc.index` | Indexer des documents (RAG) | writer | `{user, agent, collection, documents[]}` |
| `doc.query` | Requêter la collection | reader | `{user, collection, query, n_results?}` |
| `n8n.trigger` | Déclencher un workflow n8n | writer | `{user, agent, payload?, idempotency_key?}` |
| `git.commit_push` | Commit & push des fichiers listés | writer | `{user, agent, branch, paths[], message, idempotency_key?}` |
| `conversation.snapshot.save` | Sauver un snapshot conversationnel | writer | `{user, agent, namespace, summary_hint?}` |

## 4. Règles appliquées par le sidecar

- **Charte** : chaque appel consigne un événement `charter_read` (hash de `docs/charte.md`).
- **RBAC** : l’entête `X-ROLE` est injecté (`reader` ou `writer`).
- **Rate-limit** : 5 requêtes/10 s par couple (tool, agent).
- **Politique FS** : écriture limitée à `/projects`, `/reports`, `/students`, `/memory` + nommage `YYYYMMDD_agent_topic__slug.md`.
- **metadata.source** obligatoire pour `doc.index` (doit pointer vers une ressource autorisée).

## 5. Smoketest rapide

```bash
python scripts/smoke_mcp.py
```

- Vérifie lecture/écriture fichiers
- Indexation/query RAG avec `source`
- Déclencheur n8n (réponse informative si webhook absent)
- Simulation commit git
- Sauvegarde snapshot

## 6. Notes

- Le sidecar s’appuie sur l’API FastAPI locale (`SENTRA_API_BASE`, défaut `http://api:8000`).
- Ajustez les allowlists via `FS_ROOTS_ALLOW` et `FS_NAMING` si besoin.
- Les logs d’éthique s’écrivent dans `memory/audit.ndjson` (ou `stdout` si dossier absent).
- Le serveur MCP expose un endpoint SSE sur \\/mcp\\ et un healthcheck sur \\/healthz\\.
