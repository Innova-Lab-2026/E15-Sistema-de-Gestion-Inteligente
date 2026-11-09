"""Per-client rate limit for the endpoints that call external services (LLM, USIG, epok).

A sliding one-minute window per client IP, kept in memory. Enough for a single-instance MVP:
with several workers or instances each one counts on its own (move to Redis if that changes).

The client IP is `request.client.host`. Behind a reverse proxy, run uvicorn with proxy headers
(FORWARDED_ALLOW_IPS) so that value is the real client and not the proxy.
"""

from __future__ import annotations

import math
import time
from collections import deque

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.errors import AppError, ErrorCode

WINDOW_SECONDS = 60.0
_MAX_TRACKED_CLIENTS = 10_000


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = {}

    def hit(self, key: str, limit: int, now: float | None = None) -> float | None:
        """Registers a hit. Returns None if allowed, or the seconds to wait if over the limit."""
        now = time.monotonic() if now is None else now
        window_start = now - WINDOW_SECONDS
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= window_start:
            hits.popleft()
        if len(hits) >= limit:
            return hits[0] - window_start
        hits.append(now)
        if len(self._hits) > _MAX_TRACKED_CLIENTS:
            self._prune(window_start)
        return None

    def _prune(self, window_start: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= window_start]:
            del self._hits[key]

    def reset(self) -> None:
        self._hits.clear()


limiter = SlidingWindowLimiter()


async def enforce_rate_limit(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if not settings.rate_limit_enabled:
        return
    client = request.client.host if request.client else "unknown"
    wait = limiter.hit(client, settings.rate_limit_per_minute)
    if wait is not None:
        raise AppError(
            ErrorCode.RATE_LIMITED,
            {"limit_per_minute": settings.rate_limit_per_minute},
            headers={"Retry-After": str(max(1, math.ceil(wait)))},
        )
