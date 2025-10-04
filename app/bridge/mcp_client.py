from __future__ import annotations

from typing import Any, Dict, List

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult, Tool

from app.core.config import get_settings


class MCPBridgeError(RuntimeError):
    """Raised when an MCP bridge operation fails."""


async def _ensure_messages_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/messages"):
        return f"{base}/"
    if base.endswith("/messages/"):
        return base
    return f"{base}/messages/"


async def list_tools() -> List[Tool]:
    settings = get_settings()
    timeout = float(settings.mcp_bridge_timeout_seconds)
    messages_url = await _ensure_messages_url(settings.mcp_gateway_base_url)
    try:
        async with streamablehttp_client(messages_url, timeout=timeout, sse_read_timeout=timeout) as (
            read_stream,
            write_stream,
            _,
        ):
            session = ClientSession(read_stream, write_stream)
            await session.initialize()
            result = await session.list_tools()
            return list(result.tools or [])
    except Exception as exc:  # pragma: no cover - network/runtime issues propagated
        raise MCPBridgeError(str(exc)) from exc


async def call_tool(tool: str, arguments: Dict[str, Any]) -> CallToolResult:
    settings = get_settings()
    timeout = float(settings.mcp_bridge_timeout_seconds)
    messages_url = await _ensure_messages_url(settings.mcp_gateway_base_url)
    try:
        async with streamablehttp_client(messages_url, timeout=timeout, sse_read_timeout=timeout) as (
            read_stream,
            write_stream,
            _,
        ):
            session = ClientSession(read_stream, write_stream)
            await session.initialize()
            await session.list_tools()  # refresh schema cache
            result = await session.call_tool(tool, arguments, read_timeout_seconds=None)
            return result
    except Exception as exc:  # pragma: no cover - network/runtime issues propagated
        raise MCPBridgeError(str(exc)) from exc
