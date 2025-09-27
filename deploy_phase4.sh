#!/bin/bash
set -euo pipefail

echo "=== [1] Sauvegarde .env ==="
cp -n .env .env.bak_$(date +%F_%H-%M) || true

echo "=== [2] Pull dernière version main ==="
git fetch --all --tags
git checkout main
git pull --ff-only origin main

echo "=== [3] Rebuild API sans cache ==="
docker compose --env-file .env build --no-cache api

echo "=== [4] Relance API ==="
docker compose --env-file .env up -d api

echo "=== [5] Vérification OpenAPI BusSendResponse ==="
curl -s http://127.0.0.1:${API_HOST_PORT:-8012}/openapi.json \
| jq '.components.schemas.BusSendResponse'
