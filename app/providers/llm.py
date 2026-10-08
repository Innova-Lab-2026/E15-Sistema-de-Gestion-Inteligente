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
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.exception("LLM request failed")
            raise LLMUnavailableError(str(exc)) from exc

        try:
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, list):
                # Some providers return content parts
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            logger.exception("LLM returned unparseable JSON")
            raise LLMUnavailableError("LLM returned invalid JSON") from exc
