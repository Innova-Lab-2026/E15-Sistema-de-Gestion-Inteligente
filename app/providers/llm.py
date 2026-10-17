"""OpenAI-compatible LLM client (Gemini / OpenRouter / etc.)."""

from __future__ import annotations

import json
import logging
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


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = (settings.llm_base_url or "").rstrip("/")
        self.api_key = settings.llm_api_key or ""
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    async def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        if not self.is_configured:
            raise LLMUnavailableError("LLM_BASE_URL / LLM_API_KEY not configured")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
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
