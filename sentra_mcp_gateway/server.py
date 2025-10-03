from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi_mcp.types import HTTPRequestInfo
import mcp.types as mcp_types

from app.main import create_app
from sentra_mcp_gateway.middleware.ethics import log_charter_read
from sentra_mcp_gateway.middleware.rate_limit import RateLimitError, RateLimiter
from sentra_mcp_gateway.policies import fs_policy

API_BASE = os.getenv("SENTRA_API_BASE", "http://api:8000").rstrip("/")
RATE_LIMIT = int(os.getenv("MCP_RATE_LIMIT", "5"))
RATE_WINDOW_SECONDS = int(os.getenv("MCP_RATE_WINDOW_SECONDS", "10"))

INCLUDED_OPERATIONS = [
    "files.read",
    "files.write",
    "rag.index",
    "rag.query",
    "n8n.trigger",
    "git.commitPush",
]

TOOL_ALIASES: Dict[str, str] = {
    "rag.index": "doc.index",
    "rag.query": "doc.query",
    "git.commitPush": "git.commit_push",
}

ECHO_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "title": "sentra.echoArguments",
    "additionalProperties": False,
    "properties": {
        "message": {"type": "string", "description": "Message to echo back"},
    },
    "required": ["message"],
}

ECHO_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "title": "sentra.echoResult",
    "additionalProperties": False,
    "properties": {
        "message": {"type": "string"},
    },
    "required": ["message"],
}


RATE_POLICIES: Dict[str, Dict[str, Any]] = {
    "files.read": {"subject": ["user"], "role": "reader", "user": ["user"], "agent": None},
    "files.write": {"subject": ["agent"], "role": "writer", "user": ["user"], "agent": ["agent"]},
    "doc.index": {"subject": ["agent"], "role": "writer", "user": ["user"], "agent": ["agent"]},
    "doc.query": {"subject": ["user"], "role": "reader", "user": ["user"], "agent": None},
    "n8n.trigger": {"subject": ["agent"], "role": "writer", "user": ["user"], "agent": ["agent"]},
    "git.commit_push": {"subject": ["agent"], "role": "writer", "user": ["user"], "agent": ["agent"]},
    "conversation.snapshot.save": {"subject": ["agent"], "role": "writer", "user": ["user"], "agent": ["agent"]},
    "sentra.echo": {"subject": None, "role": "reader", "user": None, "agent": None},
}

SNAPSHOT_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "title": "conversation.snapshot.saveArguments",
    "additionalProperties": False,
    "properties": {
        "user": {"type": "string", "minLength": 1, "description": "User identifier"},
        "agent": {"type": "string", "minLength": 1, "description": "Agent name creating the snapshot"},
        "namespace": {
            "type": "string",
            "minLength": 1,
            "description": "Snapshot namespace used for folder and filename",
        },
        "summary_hint": {"type": "string", "description": "Optional short summary appended to the snapshot body"},
    },
    "required": ["user", "agent", "namespace"],
}

SNAPSHOT_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "title": "conversation.snapshot.saveResult",
    "additionalProperties": False,
    "properties": {
        "snapshot_path": {"type": "string", "description": "Absolute path to the snapshot markdown file"},
    },
    "required": ["snapshot_path"],
}


class SentraFastApiMCP(FastApiMCP):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._tool_aliases = TOOL_ALIASES
        self._rate_limiter = RateLimiter(limit=RATE_LIMIT, window_seconds=RATE_WINDOW_SECONDS)
        super().__init__(*args, **kwargs)
        self._apply_aliases()
        self._register_snapshot_tool()
        self._register_echo_tool()

    def _apply_aliases(self) -> None:
        for original, alias in self._tool_aliases.items():
            if original not in self.operation_map:
                continue
            if alias in self.operation_map:
                continue
            self.operation_map[alias] = self.operation_map.pop(original)
            for tool in self.tools:
                if tool.name == original:
                    tool.name = alias
                    break

    def _register_snapshot_tool(self) -> None:
        snapshot_tool = mcp_types.Tool(
            name="conversation.snapshot.save",
            description="Create or update a markdown snapshot under /memory/snapshots/{namespace}.",
            inputSchema=SNAPSHOT_INPUT_SCHEMA,
            outputSchema=SNAPSHOT_OUTPUT_SCHEMA,
        )
        if all(tool.name != snapshot_tool.name for tool in self.tools):
            self.tools.append(snapshot_tool)
        self.operation_map.setdefault("conversation.snapshot.save", {"custom": True})
        self.tools.sort(key=lambda tool: tool.name)

    def _register_echo_tool(self) -> None:
        echo_tool = mcp_types.Tool(
            name="sentra.echo",
            description="Echo back a test message to validate MCP connectivity.",
            inputSchema=ECHO_INPUT_SCHEMA,
            outputSchema=ECHO_OUTPUT_SCHEMA,
        )
        if all(tool.name != echo_tool.name for tool in self.tools):
            self.tools.append(echo_tool)
        self.operation_map.setdefault("sentra.echo", {"custom": True})
        self.tools.sort(key=lambda tool: tool.name)

    @staticmethod
    def _merge_headers(http_info: Optional[HTTPRequestInfo], extra: Dict[str, str]) -> HTTPRequestInfo:
        if http_info:
            headers = dict(http_info.headers or {})
            headers.update(extra)
            return HTTPRequestInfo(
                method=http_info.method,
                path=http_info.path,
                headers=headers,
                cookies=dict(http_info.cookies or {}),
                query_params=dict(http_info.query_params or {}),
                body=http_info.body,
            )
        return HTTPRequestInfo(
            method="POST",
            path="/",
            headers=extra,
            cookies={},
            query_params={},
            body=None,
        )

    @staticmethod
    def _extract(arguments: Dict[str, Any], path: Optional[List[str]]) -> Optional[Any]:
        if not path:
            return None
        value: Any = arguments
        for key in path:
            if not isinstance(value, dict):
                return None
            value = value.get(key)
        return value

    def _enforce_policy(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Optional[str]]:
        policy = RATE_POLICIES.get(tool_name)
        if not policy:
            return {"role": None, "user": None, "agent": None}
        user = self._extract(arguments, policy.get("user"))
        agent = self._extract(arguments, policy.get("agent"))
        subject = self._extract(arguments, policy.get("subject")) or agent or user or ""
        try:
            self._rate_limiter.hit(tool_name, str(subject or ""))
        except RateLimitError as error:
            raise Exception(str(error)) from error
        if not user:
            raise Exception("The 'user' field is required for this tool.")
        log_charter_read(tool_name, str(user), str(agent) if agent is not None else None)
        return {"role": policy.get("role"), "user": str(user), "agent": str(agent) if agent is not None else None}

    def _transform_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        transformed = dict(arguments or {})
        if tool_name == "files.read":
            path = transformed.get("path")
            if path:
                try:
                    transformed["path"] = str(fs_policy.ensure_library_path(str(path)))
                except ValueError as error:
                    raise Exception(str(error)) from error
        elif tool_name == "files.write":
            path = transformed.get("path")
            agent = transformed.get("agent")
            if path and agent:
                topic_hint = Path(str(path)).stem or "note"
                try:
                    transformed["path"] = str(
                        fs_policy.ensure_library_path(str(path), agent=str(agent), topic=topic_hint)
                    )
                except ValueError as error:
                    raise Exception(str(error)) from error
        elif tool_name == "doc.index":
            documents = transformed.get("documents") or []
            if not isinstance(documents, list):
                raise Exception("documents must be a list")
            sanitized_docs: List[Dict[str, Any]] = []
            for raw_doc in documents:
                if not isinstance(raw_doc, dict):
                    raise Exception("Each document must be an object")
                metadata = dict(raw_doc.get("metadata") or {})
                source = metadata.get("source")
                if not source:
                    raise Exception("metadata.source is required for doc.index")
                try:
                    source_path = fs_policy.ensure_library_path(str(source))
                    metadata = fs_policy.ensure_metadata_source(metadata, source_path)
                except ValueError as error:
                    raise Exception(str(error)) from error
                sanitized_docs.append(
                    {
                        "text": raw_doc.get("text"),
                        "metadata": metadata,
                        "id": raw_doc.get("id"),
                    }
                )
            transformed["documents"] = sanitized_docs
        return transformed

    async def _execute_api_tool(
        self,
        client: httpx.AsyncClient,
        tool_name: str,
        arguments: Dict[str, Any],
        operation_map: Dict[str, Dict[str, Any]],
        http_request_info: Optional[HTTPRequestInfo] = None,
    ) -> List[mcp_types.TextContent]:
        arguments = dict(arguments or {})
        policy = self._enforce_policy(tool_name, arguments)
        transformed_args = self._transform_arguments(tool_name, arguments)
        if tool_name == "conversation.snapshot.save":
            return await self._handle_snapshot(transformed_args)
        if tool_name == "sentra.echo":
            return self._handle_echo(transformed_args)
        headers: Dict[str, str] = {}
        role = policy.get("role")
        if role:
            headers["X-ROLE"] = str(role)
        merged_info = self._merge_headers(http_request_info, headers) if headers else http_request_info
        return await super()._execute_api_tool(client, tool_name, transformed_args, operation_map, merged_info)

    async def _handle_snapshot(self, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
        namespace = arguments.get("namespace")
        agent = arguments.get("agent")
        user = arguments.get("user")
        summary_hint = arguments.get("summary_hint")
        if not namespace:
            raise Exception("namespace is required")
        if not agent:
            raise Exception("agent is required")
        if not user:
            raise Exception("user is required")
        try:
            target_path = fs_policy.ensure_library_path(
                f"/memory/snapshots/{namespace}/{namespace}.md",
                agent=str(agent),
                topic=str(namespace),
            )
        except ValueError as error:
            raise Exception(str(error)) from error
        lines = [
            f"# Snapshot {namespace}",
            "",
            f"Agent: {agent}",
            f"User: {user}",
        ]
        if summary_hint:
            lines.extend(["", f"Summary: {summary_hint}"])
        payload = {
            "user": user,
            "agent": agent,
            "path": str(target_path),
            "content": "\n".join(lines) + "\n",
        }
        response = await self._request(
            self._http_client,
            method="post",
            path="/files/write",
            query={},
            headers={"X-ROLE": "writer"},
            body=payload,
        )
        try:
            body = response.json()
        except json.JSONDecodeError:
            raw_payload = response.text if hasattr(response, "text") else str(response.content)
            raise Exception(
                f"conversation.snapshot.save returned an unexpected payload: {raw_payload}"
            )
        if 400 <= response.status_code < 600:
            serialized = json.dumps(body, indent=2, ensure_ascii=False)
            raise Exception(
                f"Error calling conversation.snapshot.save. Status code: {response.status_code}. Response: {serialized}"
            )
        snapshot_path = body.get("path") if isinstance(body, dict) else None
        result = {"snapshot_path": snapshot_path}
        return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    def _handle_echo(self, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
        message = arguments.get("message")
        if message is None or not isinstance(message, str) or not message.strip():
            raise Exception("message is required and must be a non-empty string")
        payload = json.dumps({"message": message}, indent=2, ensure_ascii=False)
        return [mcp_types.TextContent(type="text", text=payload)]


def create_mcp_app() -> FastAPI:
    api_app = create_app()
    http_client = httpx.AsyncClient(base_url=API_BASE, timeout=10.0)
    mcp_server = SentraFastApiMCP(
        api_app,
        name="SENTRA MCP",
        description="SENTRA tools exposed through MCP",
        http_client=http_client,
        include_operations=INCLUDED_OPERATIONS,
    )
    app = FastAPI(title="SENTRA MCP Gateway", version="1.0.0")

    mcp_server.mount(app, mount_path="/mcp")

    app.state.http_client = http_client
    app.state.mcp_server = mcp_server

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await http_client.aclose()

    @app.get("/", include_in_schema=False)
    async def root() -> Dict[str, str]:
        return {"status": "ok", "mcp": "/mcp"}

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> Dict[str, str]:
        return {"status": "ok"}

    return app


app = create_mcp_app()
