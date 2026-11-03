"""Cliente BA Data (CKAN) — siempre con User-Agent (WAF)."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings

DEFAULT_UA = "Mozilla/5.0 (compatible; InobaLab-TECBA/1.0; +https://github.com/InobaLab)"


class BaDataClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ba_data_base_url.rstrip("/")
        self.timeout = settings.ba_data_timeout_seconds
        self.user_agent = settings.ba_data_user_agent or DEFAULT_UA

    @property
    def _headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    async def package_show(self, package_id: str) -> dict[str, Any] | None:
        url = f"{self.base_url}/api/3/action/package_show"
        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self._headers, follow_redirects=True
        ) as client:
            response = await client.get(url, params={"id": package_id})
            response.raise_for_status()
            payload = response.json()
            if not payload.get("success"):
                return None
            result = payload.get("result")
            return result if isinstance(result, dict) else None

    async def package_list(self) -> list[str]:
        url = f"{self.base_url}/api/3/action/package_list"
        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self._headers, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
            if not payload.get("success"):
                return []
            result = payload.get("result") or []
            return [str(x) for x in result]


def summarize_package(pkg: dict[str, Any]) -> dict[str, Any]:
    org = pkg.get("organization") or {}
    resources = []
    for res in pkg.get("resources") or []:
        resources.append(
            {
                "id": res.get("id"),
                "name": res.get("name"),
                "format": res.get("format"),
                "url": res.get("url"),
                "description": res.get("description"),
            }
        )
    return {
        "id": pkg.get("name") or pkg.get("id"),
        "title": pkg.get("title"),
        "notes": (pkg.get("notes") or "")[:500],
        "organization": org.get("title") if isinstance(org, dict) else None,
        "license_id": pkg.get("license_id"),
        "metadata_created": pkg.get("metadata_created"),
        "metadata_modified": pkg.get("metadata_modified"),
        "url": f"https://data.buenosaires.gob.ar/dataset/{pkg.get('name')}",
        "resources": resources,
    }
