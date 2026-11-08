"""OpenAI-compatible LLM client (Gemini / OpenRouter / etc.)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)


class LLMUnavailableError(Exception):
    """Raised when the LLM provider cannot be reached or is misconfigured."""

    reason = "llm_unavailable"


class LLMRateLimitedError(LLMUnavailableError):
    """HTTP 429: provider quota exhausted (free tiers have low RPM/TPM limits)."""

    reason = "llm_rate_limited"

    def __init__(self, retry_after: str | None) -> None:
        self.retry_after = retry_after
        super().__init__(f"LLM rate limited (retry-after={retry_after})")


class LLMInvalidOutputError(LLMUnavailableError):
    """The provider answered, but not with the expected JSON object."""

    reason = "llm_invalid_output"


@dataclass(frozen=True)
class LLMEndpoint:
    name: str  # "primary" | "fallback"
    base_url: str
    api_key: str
    model: str


class LLMClient:
    """Chain of OpenAI-compatible providers: the main LLM, then the backup (B17)."""

    def __init__(self, settings: Settings) -> None:
        self.timeout = settings.llm_timeout_seconds
        candidates = [
            LLMEndpoint("primary", settings.llm_base_url, settings.llm_api_key, settings.llm_model),
            LLMEndpoint(
                "fallback",
                settings.llm_fallback_base_url,
                settings.llm_fallback_api_key,
                settings.llm_fallback_model or settings.llm_model,
            ),
        ]
        self.endpoints = [
            LLMEndpoint(e.name, (e.base_url or "").rstrip("/"), e.api_key or "", e.model)
            for e in candidates
            if e.base_url and e.api_key
        ]
        self.model = settings.llm_model
        # Model that produced the last answer (for logs and the consultation record).
        self.last_model: str | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoints)

    async def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        if not self.endpoints:
            raise LLMUnavailableError("LLM_BASE_URL / LLM_API_KEY not configured")
        last_error: LLMUnavailableError | None = None
        for endpoint in self.endpoints:
            try:
                result = await self._complete_json(endpoint, system_prompt=system_prompt, user_prompt=user_prompt)
            except LLMUnavailableError as exc:
                last_error = exc
                logger.warning("LLM %s (%s) failed: %s", endpoint.name, endpoint.model, exc.reason)
                continue
            self.last_model = endpoint.model
            logger.info("LLM answered with %s (%s)", endpoint.model, endpoint.name)
            return result
        assert last_error is not None
        raise last_error

    async def _complete_json(
        self,
        endpoint: LLMEndpoint,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        url = f"{endpoint.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {endpoint.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": endpoint.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 429:
                    raise LLMRateLimitedError(response.headers.get("retry-after"))
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("LLM request failed: %r", exc)
            raise LLMUnavailableError(str(exc)) from exc
        except ValueError as exc:  # body is not JSON
            raise LLMInvalidOutputError("LLM response is not JSON") from exc

        try:
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                # Some providers return content parts
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            parsed = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            logger.warning("LLM returned unparseable JSON: %r", exc)
            raise LLMInvalidOutputError("LLM returned invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise LLMInvalidOutputError("LLM returned JSON that is not an object")
        return parsed
