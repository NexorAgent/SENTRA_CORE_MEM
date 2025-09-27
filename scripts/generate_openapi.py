import json
import sys
import types
from pathlib import Path
from typing import Any, Dict


CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _install_google_stubs() -> None:
    if "google.oauth2.service_account" in sys.modules:
        return

    google_module = sys.modules.setdefault("google", types.ModuleType("google"))
    oauth2_module = sys.modules.setdefault("google.oauth2", types.ModuleType("google.oauth2"))
    service_account_module = types.ModuleType("google.oauth2.service_account")

    class DummyCredentials:
        @classmethod
        def from_service_account_file(cls, *args, **kwargs):
            return cls()

    service_account_module.Credentials = DummyCredentials
    oauth2_module.service_account = service_account_module
    setattr(google_module, "oauth2", oauth2_module)
    sys.modules["google.oauth2"] = oauth2_module
    sys.modules["google.oauth2.service_account"] = service_account_module


def _install_googleapiclient_stubs() -> None:
    required_modules = {
        "googleapiclient.discovery",
        "googleapiclient.http",
        "googleapiclient.errors",
    }
    if required_modules.issubset(sys.modules.keys()):
        return

    googleapiclient_module = sys.modules.setdefault(
        "googleapiclient", types.ModuleType("googleapiclient")
    )

    class DummyService:
        def __getattr__(self, _name):
            def _call(*args, **kwargs):
                return self

            return _call

    def build(*args, **kwargs):
        return DummyService()

    discovery_module = types.ModuleType("googleapiclient.discovery")
    discovery_module.build = build
    sys.modules["googleapiclient.discovery"] = discovery_module
    setattr(googleapiclient_module, "discovery", discovery_module)

    http_module = types.ModuleType("googleapiclient.http")

    class MediaInMemoryUpload:
        def __init__(self, *args, **kwargs):
            pass

    http_module.MediaInMemoryUpload = MediaInMemoryUpload
    sys.modules["googleapiclient.http"] = http_module
    setattr(googleapiclient_module, "http", http_module)

    errors_module = types.ModuleType("googleapiclient.errors")

    class HttpError(Exception):
        pass

    errors_module.HttpError = HttpError
    sys.modules["googleapiclient.errors"] = errors_module
    setattr(googleapiclient_module, "errors", errors_module)


def _install_chromadb_stub() -> None:
    if "chromadb" in sys.modules:
        return
    try:
        import chromadb  # type: ignore
    except ModuleNotFoundError:
        chromadb_module = types.ModuleType("chromadb")

        class DummyCollection:
            def upsert(self, *args, **kwargs):
                return None

            def query(self, *args, **kwargs):
                return {}

        class DummyClient:
            def __init__(self, *args, **kwargs):
                pass

            def get_or_create_collection(self, name):
                return DummyCollection()

        chromadb_module.PersistentClient = DummyClient
        sys.modules["chromadb"] = chromadb_module
    else:
        sys.modules.setdefault("chromadb", chromadb)


def ensure_optional_dependencies() -> None:
    try:
        import google.oauth2.service_account  # type: ignore
    except ModuleNotFoundError:
        _install_google_stubs()

    try:
        import googleapiclient.discovery  # type: ignore
        import googleapiclient.http  # type: ignore
        import googleapiclient.errors  # type: ignore
    except ModuleNotFoundError:
        _install_googleapiclient_stubs()

    _install_chromadb_stub()


def build_schema() -> Dict[str, Any]:
    ensure_optional_dependencies()

    from app.main import create_app

    app = create_app()
    schema = app.openapi()
    schema["servers"] = [{"url": "http://localhost:5000"}]
    return schema


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
    schema = build_schema()
    output_path = Path(__file__).resolve().parents[1] / "openapi.yaml"
    yaml_content = dump_yaml(schema) + "\n"
    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"OpenAPI schema written to {output_path}")


if __name__ == "__main__":
    main()
