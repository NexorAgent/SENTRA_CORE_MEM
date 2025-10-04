from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.bridge.mcp_client import MCPBridgeError, call_tool, list_tools

router = APIRouter(prefix="/bridge/mcp", tags=["mcp-bridge"])


class ToolDescriptor(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = Field(default=None, alias="inputSchema")
    output_schema: Optional[Dict[str, Any]] = Field(default=None, alias="outputSchema")


class ListToolsResponse(BaseModel):
    tools: List[ToolDescriptor]


class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    tool: str
    is_error: bool = Field(alias="isError")
    content: List[Dict[str, Any]] = Field(default_factory=list)
    structured_content: Optional[Any] = Field(default=None, alias="structuredContent")
    error: Optional[Dict[str, Any]] = None


def _serialize_tool(tool) -> ToolDescriptor:
    return ToolDescriptor(
        name=tool.name,
        description=getattr(tool, "description", None),
        input_schema=getattr(tool, "inputSchema", None),
        output_schema=getattr(tool, "outputSchema", None),
    )


def _serialize_call_result(tool: str, result) -> ToolCallResponse:
    serialized_content: List[Dict[str, Any]] = []
    if result.content:
        serialized_content = [item.model_dump(mode="json") for item in result.content]
    serialized_error: Optional[Dict[str, Any]] = None
    if result.error:
        serialized_error = result.error.model_dump(mode="json")
    return ToolCallResponse(
        tool=tool,
        isError=bool(result.isError),
        content=serialized_content,
        structuredContent=result.structuredContent,
        error=serialized_error,
    )


@router.get("/tools", response_model=ListToolsResponse)
async def bridge_list_tools() -> ListToolsResponse:
    try:
        tools = await list_tools()
    except MCPBridgeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ListToolsResponse(tools=[_serialize_tool(tool) for tool in tools])


@router.post("/tools/call", response_model=ToolCallResponse)
async def bridge_call_tool(request: ToolCallRequest) -> ToolCallResponse:
    try:
        result = await call_tool(request.tool, request.arguments)
    except MCPBridgeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _serialize_call_result(request.tool, result)
