"""Shared outbound HTTP client for official GCBA sources (USIG, epok).

One AsyncClient per process, opened in the app lifespan: reuses connections and always sends a
User-Agent (the GCBA WAF rejects some requests without one) and retries connection failures.
Timeouts stay per provider and are passed on each request.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from app.core.config import Settings

_client: httpx.AsyncClient | None = None


def _build(settings: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": settings.http_user_agent},
        timeout=settings.http_timeout_seconds,
        transport=httpx.AsyncHTTPTransport(retries=settings.http_retries),
    )


async def open_http_client(settings: Settings) -> None:
    global _client
    await close_http_client()
    _client = _build(settings)


async def close_http_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_http_client(settings: Settings) -> httpx.AsyncClient:
    """Client opened by the lifespan; created lazily when providers run outside the app (scripts)."""
    global _client
    if _client is None:
        _client = _build(settings)
    return _client


@asynccontextmanager
async def shared_http_client(settings: Settings) -> AsyncIterator[httpx.AsyncClient]:
    """Drop-in for `async with httpx.AsyncClient(...)`: yields the shared client without closing it."""
    yield get_http_client(settings)
