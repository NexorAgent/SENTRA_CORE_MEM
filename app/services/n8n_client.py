from __future__ import annotations

from typing import Any, Dict
import os

import requests


class N8NConfigurationError(RuntimeError):
    pass


class N8NClient:
    def __init__(self, webhook_url: str | None = None, timeout: int = 10) -> None:
        self._webhook_url = webhook_url or os.getenv("N8N_WEBHOOK_URL")
        self._timeout = timeout
        if not self._webhook_url:
            raise N8NConfigurationError("N8N webhook URL is not configured")

    def trigger(self, payload: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        response = requests.post(self._webhook_url, json=payload, headers=headers, timeout=self._timeout)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return {"status_code": response.status_code, "content": response.text}
