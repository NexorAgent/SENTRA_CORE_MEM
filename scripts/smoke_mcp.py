#!/usr/bin/env python
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import anyio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:8400").rstrip("/")
USER = os.getenv("MCP_USER", "ops")
AGENT = os.getenv("MCP_AGENT", "dispatcher")

EXPECTED_TOOLS = [
    "files.read",
    "files.write",
    "doc.index",
    "doc.query",
    "n8n.trigger",
    "git.commit_push",
    "conversation.snapshot.save",
]


async def call_and_report(session: ClientSession, name: str, arguments: Dict[str, Any]) -> None:
    print(f"[SMOKE] {name}")
    try:
        result = await session.call_tool(name, arguments)
    except Exception as exc:  # pragma: no cover - diagnostic utility
        print(f"  ERROR: {exc}")
        return

    if result.isError:
        print(f"  ERROR: {json.dumps(result.model_dump(mode='json'), indent=2)}")
        return

    if result.structuredContent:
        print(f"  structured:\n{json.dumps(result.structuredContent, indent=2, ensure_ascii=False)}")

    def iter_text(blocks: Iterable[types.ContentBlock]) -> List[str]:
        texts: List[str] = []
        for block in blocks:
            if isinstance(block, types.TextContent):
                payload = block.text.strip()
                if payload:
                    texts.append(payload)
        return texts

    for line in iter_text(result.content or []):
        print(f"  text: {line}")


async def smoke() -> None:
    endpoint = f"{BASE_URL}/mcp"
    print(f"Connecting to {endpoint}")
    async with sse_client(endpoint) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = sorted(tool.name for tool in listed.tools)
            missing = [tool for tool in EXPECTED_TOOLS if tool not in names]
            if missing:
                print(f"Missing tools: {', '.join(missing)}")
            else:
                print(f"Tools available: {', '.join(names)}")

            temp_path = "/projects/smokes/snapshot.md"
            await call_and_report(
                session,
                "files.write",
                {
                    "user": USER,
                    "agent": AGENT,
                    "path": temp_path,
                    "content": "Smoke test MCP\n",
                },
            )
            await call_and_report(
                session,
                "files.read",
                {
                    "user": USER,
                    "path": temp_path,
                },
            )
            await call_and_report(
                session,
                "doc.index",
                {
                    "user": USER,
                    "agent": AGENT,
                    "collection": "smoke",
                    "documents": [
                        {"text": "Doc identique", "metadata": {"source": "/projects/smokes/doc1.md"}},
                        {"text": "Doc identique", "metadata": {"source": "/projects/smokes/doc2.md"}},
                    ],
                },
            )
            await call_and_report(
                session,
                "doc.query",
                {
                    "user": USER,
                    "collection": "smoke",
                    "query": "Doc",
                    "n_results": 3,
                },
            )
            await call_and_report(
                session,
                "n8n.trigger",
                {
                    "user": USER,
                    "agent": AGENT,
                    "payload": {"check": "smoke"},
                },
            )
            await call_and_report(
                session,
                "git.commit_push",
                {
                    "user": USER,
                    "agent": AGENT,
                    "branch": "main",
                    "paths": ["README.md"],
                    "message": "smoke",
                },
            )
            await call_and_report(
                session,
                "conversation.snapshot.save",
                {
                    "user": USER,
                    "agent": AGENT,
                    "namespace": "smoke",
                    "summary_hint": "test snapshot",
                },
            )


if __name__ == "__main__":
    anyio.run(smoke)
