from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple


class RateLimitError(RuntimeError):
    pass


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 10) -> None:
        self._limit = limit
        self._window = window_seconds
        self._hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    def hit(self, tool: str, agent: str) -> None:
        now = time.monotonic()
        key = (tool, agent or "")
        bucket = self._hits[key]
        bucket.append(now)
        while bucket and now - bucket[0] > self._window:
            bucket.popleft()
        if len(bucket) > self._limit:
            raise RateLimitError(
                f"Rate limit dépassé pour {tool} par {agent or 'inconnu'} ({self._limit}/{self._window}s)"
            )

    def reset(self) -> None:
        self._hits.clear()
