# SENTRA SBX2 — Routes OAuth & RBAC

## RBAC
- `X-ROLE: Writer` ou `Owner` obligatoire pour les routes Google.
- Sans rôle → **403**, refus journalisé dans `memory/audit.ndjson`.

## Endpoints Drive
- `POST /google/gdrive/upload`
- `POST /google/gdrive/upload_oauth`

## Endpoints Calendar
- `POST /google/gcal/create_event`

## Endpoints ZEP
- `POST /zep/save`
- `GET /zep/search`

## Endpoint Divers
- `POST /correct_file`
- `GET /` (ping)
