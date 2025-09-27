# SENTRA_CORE_MEM - Modular AI Orchestrator

## Vision Overview
Build a disciplined, modular orchestration layer (SENTRA_CORE_MEM) running on a VPS that can:
- Manage hybrid persistent memory (VPS core, Google Drive backup, future Zep vector store).
- Drive n8n workflows (Google, Notion, Discord, Telegram, WhatsApp, ...).
- Deliver a multi-function personal assistant (notes, file creation, automated actions).
- Enforce a strict IA charter for consistency and auditability.
- Grow into an external MCP orchestrator when classic APIs disappear.

---

## File Organization
- Every file has one canonical location, like a library shelf.
- Natural language creates structure: "Create `projects/2025/notes/brief.md`."
- Reading/search uses explicit paths: "Read `projects/2025/notes/brief.md`."
- Markdown as default format for uniformity.
- Transient logs or artifacts stay out of the main memory tree.

---

## IA Conduct Rules
- The IA charter is read before every interaction.
- Every 30 interactions:
  - Persist the current thread memory in `/memory/` and on Drive.
  - Re-read context to avoid drift.
- RBAC plus NDJSON audit logging remain active at all times.

---

## Connectors
- Google Sheets (bus slim, bi-directional comms).
- Google Drive (document storage).
- Google Calendar (events).
- n8n webhooks and orchestrations.
- Upcoming: Discord, Telegram, WhatsApp, Notion, Revit API.

---

## Persistent Memory Options
| Option | Advantage | Drawback |
|--------|-----------|----------|
| Zep / external vector store | Native indexing | External dependency |
| Google Drive raw storage | Capacity, redundancy | Manual triage/search |
| VPS local store | Full control, speed | Requires indexing (Chroma/FAISS) |

Hybrid approach: VPS for operations, Drive for backups, Zep for scale.

---

## GPT and MCP
- ChatGPT (Developer Mode) acts as the daily orchestrator.
- GPT writes notes, creates files, triggers n8n workflows.
- MCP layer will pilot Notion, Google, Revit using the same pattern.

---

## Personal Teacher Agent
- Dedicated teaching agent with its own course base.
- Builds long learning plans, tracks progress, generates tests and cases.
- Pedagogic memory isolated in `/memory/courses/`.

---

## Security and Discipline
- RBAC enforced (owner / writer / reader / system).
- Continuous NDJSON audit trail.
- Drive snapshots plus log rotation.
- Cloudflare tunnel and firewall active.

---

## Roadmap by Phase
| Phase | Status | Highlights |
|-------|--------|------------|
| 1 - Foundations | done | Docker Compose stack (API, n8n, orchestrator, Discord, Filebrowser), FastAPI endpoints (`files`, `memory`, `bus`, `google`), GitOps and backups, network hardening |
| 2 - Connectors | in progress | Google Drive/Sheets/Calendar, n8n workflows, Discord/Telegram integrations |
| 3 - Local Memory | planned | ChromaDB indexing, Drive backups, library-style organization |
| 4 - IA Rules & API Contract | planned | Charter on each exchange, memory saved every 30 turns, bus slim responses, n8n idempotency relay, RAG results with source, files write uses text content |
| 5 - Personal Assistant | upcoming | GPT Dev Mode + MCP, WhatsApp voice to text notes, personal teacher |
| 6 - Advanced Orchestration | future | External MCP (Notion, Revit...), specialized agents (watch, SEO, BIM, automation), evolving IA governance |

---

## Tests
Pytest suite covers `files`, `memory`, `bus`, `google`, `rag`, plus an end-to-end scenario.
```bash
python -m pytest -q
python -m pytest -k bus
```

---

## Phase 4 Endpoints Snapshot

### Bus (slim contract)
```http
POST /bus/send
{
  "user": "ops",
  "agent": "dispatcher",
  "payload": {"ping": 1},
  "metadata": {"spreadsheet_id": "sheet-1", "worksheet": "Requests"},
  "idempotency_key": "ping-1"
}
=> {"message_id": "...", "status": "pending", "timestamp": "..."}
```
`/bus/poll` and `/bus/updateStatus` read the same metadata to target the Sheet.

### n8n Trigger
```http
POST /n8n/trigger
{
  "user": "ops",
  "agent": "dispatcher",
  "payload": {"action": "sync"},
  "idempotency_key": "sync-1"
}
```
Idempotency-Key is relayed only if provided.

### RAG
- `/rag/index` produces IDs from text + metadata (or honors `doc_id`).
- `/rag/query` returns `results` and filters out hits without `source`.

### Files
`files.write` accepts string `content`; `idempotency_key` remains optional.

---

## Quick Setup
1. `git clone https://github.com/NexorAgent/SENTRA_CORE_MEM.git`
2. Copy `.env.example` to `.env` and set `API_HOST_PORT`, `N8N_WEBHOOK_URL`, `BASE_DIR`, `SANDBOX_DIR`, `GOOGLE_CREDENTIALS_FILE`, ...
3. Launch the API (Docker Compose or `uvicorn app.main:app`).
4. Smoke test: `curl -sS -H "X-ROLE: writer" ... /bus/send`.

---

## Notes
This README replaces the previous DeepSeek/Phase 0 document to reflect the Phase 4 roadmap.

---

MIT License (c) 2025 SENTRA_CORE_MEM.
