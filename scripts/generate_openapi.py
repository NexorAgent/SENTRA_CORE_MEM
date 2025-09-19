"""Utility to regenerate the OpenAPI schema for the SENTRA FastAPI app."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

from fastapi.openapi.utils import get_openapi


CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.api_sentra import app

# Mapping of (HTTP method, path) to the expected MCP tool operationId.
OPERATION_IDS: Dict[Tuple[str, str], str] = {
    ("GET", "/check_env"): "checkEnv",
    ("POST", "/reprise"): "repriseProjet",
    ("POST", "/write_note"): "writeNote",
    ("GET", "/read_note"): "readNote",
    ("POST", "/move_file"): "moveFile",
    ("POST", "/write_file"): "writeFile",
    ("GET", "/get_memorial"): "getMemorial",
    ("POST", "/archive_file"): "archiveFile",
    ("GET", "/list_files"): "listFiles",
    ("GET", "/search"): "searchFiles",
    ("POST", "/delete_file"): "deleteFile",
    ("GET", "/"): "home",
    ("GET", "/status"): "status",
    ("GET", "/version"): "getVersion",
    ("GET", "/readme"): "getReadme",
    ("GET", "/logs/latest"): "getLatestLogs",
    ("GET", "/agents"): "listAgents",
    ("GET", "/explore"): "exploreProject",
    ("POST", "/correct_file"): "correctFile",
}


def apply_operation_ids(schema: Dict[str, Any]) -> None:
    paths = schema.get("paths", {})
    for path, operations in paths.items():
        for method, details in operations.items():
            key = (method.upper(), path)
            custom_id = OPERATION_IDS.get(key)
            if custom_id:
                details["operationId"] = custom_id


def ensure_servers(schema: Dict[str, Any]) -> None:
    schema["servers"] = [{"url": "http://localhost:5000"}]


def format_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def dump_yaml(data: Any, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(data, dict):
        if not data:
            return f"{prefix}{{}}"
        lines = []
        for key, value in data.items():
            key_str = str(key)
            if isinstance(value, dict):
                if not value:
                    lines.append(f"{prefix}{key_str}: {{}}")
                else:
                    lines.append(f"{prefix}{key_str}:")
                    lines.append(dump_yaml(value, indent + 1))
            elif isinstance(value, list):
                if not value:
                    lines.append(f"{prefix}{key_str}: []")
                else:
                    lines.append(f"{prefix}{key_str}:")
                    lines.append(dump_yaml(value, indent + 1))
            else:
                lines.append(f"{prefix}{key_str}: {format_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        if not data:
            return f"{prefix}[]"
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(dump_yaml(item, indent + 1))
            else:
                lines.append(f"{prefix}- {format_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{format_scalar(data)}"


def main() -> None:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    apply_operation_ids(schema)
    ensure_servers(schema)

    output_path = Path(__file__).resolve().parents[1] / "openapi.yaml"
    yaml_content = dump_yaml(schema) + "\n"
    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"OpenAPI schema written to {output_path}")


if __name__ == "__main__":
    main()
