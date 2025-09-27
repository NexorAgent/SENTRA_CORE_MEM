#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${MCP_BASE_URL:-http://localhost:8400}"
USER="${MCP_USER:-ops}"
AGENT="${MCP_AGENT:-dispatcher}"

status() {
  printf "[SMOKE] %s\n" "$1"
}

call_tool() {
  local endpoint=$1
  local payload=$2
  curl -sS -X POST "${BASE_URL}${endpoint}" \
    -H "Content-Type: application/json" \
    --data "${payload}"
}

status "files.write -> files.read"
RESP=$(call_tool "/tools/files.write" "{\"user\":\"$USER\",\"agent\":\"scribe\",\"path\":\"/projects/smokes/snapshot.md\",\"content\":\"Smoke test MCP\\n\"}")
printf "files.write => %s\n" "$RESP"

RESP=$(call_tool "/tools/files.read" "{\"user\":\"$USER\",\"path\":\"/projects/smokes/snapshot.md\"}")
printf "files.read => %s\n" "$RESP"

status "doc.index (ids distincts)"
RESP=$(call_tool "/tools/doc.index" "{\"user\":\"$USER\",\"agent\":\"scribe\",\"collection\":\"smoke\",\"documents\":[{\"text\":\"Doc identique\",\"metadata\":{\"source\":\"/projects/smokes/doc1.md\"}},{\"text\":\"Doc identique\",\"metadata\":{\"source\":\"/projects/smokes/doc2.md\"}}]}")
printf "doc.index => %s\n" "$RESP"

status "doc.query"
RESP=$(call_tool "/tools/doc.query" "{\"user\":\"$USER\",\"collection\":\"smoke\",\"query\":\"Doc\"}")
printf "doc.query => %s\n" "$RESP"

status "n8n.trigger"
RESP=$(call_tool "/tools/n8n.trigger" "{\"user\":\"$USER\",\"agent\":\"$AGENT\",\"payload\":{\"check\":\"smoke\"}}");
printf "n8n.trigger => %s\n" "$RESP"

status "git.commit_push (simulation)"
RESP=$(call_tool "/tools/git.commit_push" "{\"user\":\"$USER\",\"agent\":\"$AGENT\",\"branch\":\"main\",\"paths\":[\"README.md\"],\"message\":\"smoke\"}")
printf "git.commit_push => %s\n" "$RESP"

status "conversation.snapshot.save"
RESP=$(call_tool "/tools/conversation.snapshot.save" "{\"user\":\"$USER\",\"agent\":\"$AGENT\",\"namespace\":\"smoke\",\"summary_hint\":\"test snapshot\"}")
printf "snapshot => %s\n" "$RESP"
