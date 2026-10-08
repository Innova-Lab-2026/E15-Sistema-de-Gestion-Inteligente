from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from urllib.parse import quote

import httpx

from app.core.config import Settings


GeocodeStatus = Literal["confirmed", "ambiguous", "out_of_scope", "not_found"]


@dataclass
class GeocodeHit:
    normalized_address: str
    latitude: float
    longitude: float
    commune: str | None = None
    neighborhood: str | None = None
    city: str = "Ciudad Autonoma de Buenos Aires"
    precision: str = "rooftop"


@dataclass
class GeocodeResult:
    status: GeocodeStatus
    original_address: str
    hits: list[GeocodeHit] = field(default_factory=list)
    message: str | None = None
    provider_id: str = "geocoder"
    provider_name: str = "Geocoder"
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class GeocoderClient(ABC):
    @abstractmethod
    async def geocode(self, address: str) -> GeocodeResult:
        raise NotImplementedError


def _normalize_key(address: str) -> str:
    return " ".join(address.lower().strip().replace(",", " ").split())


def _is_caba_item(item: dict[str, Any]) -> bool:
    partido = str(item.get("cod_partido") or item.get("nombre_partido") or "").lower()
    localidad = str(item.get("nombre_localidad") or "").lower()
    direccion = str(item.get("direccion") or "").lower()
    markers = ("caba", "ciudad autonoma", "ciudad autónoma", "capital federal")
    return any(m in partido or m in localidad or m in direccion for m in markers)


class MockGeocoder(GeocoderClient):
    """Deterministic fixtures for local MVP testing."""

    FIXTURES: dict[str, GeocodeResult] = {}

    def __init__(self) -> None:
        self.FIXTURES = {
            "av. corrientes 2500": GeocodeResult(
                status="confirmed",
                original_address="Av. Corrientes 2500",
                hits=[
                    GeocodeHit(
                        normalized_address="Avenida Corrientes 2500, CABA",
                        latitude=-34.604,
                        longitude=-58.413,
                        commune="Comuna 5",
                        neighborhood="Almagro",
                        precision="rooftop",
                    )
                ],
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
            "corrientes 2500": GeocodeResult(
                status="confirmed",
                original_address="Corrientes 2500",
                hits=[
                    GeocodeHit(
                        normalized_address="Avenida Corrientes 2500, CABA",
                        latitude=-34.604,
                        longitude=-58.413,
                        commune="Comuna 5",
                        neighborhood="Almagro",
                        precision="rooftop",
                    )
                ],
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
            "av. del libertador 1954": GeocodeResult(
                status="confirmed",
                original_address="Av. del Libertador 1954",
                hits=[
                    GeocodeHit(
                        normalized_address="DEL LIBERTADOR AV. 1954, CABA",
                        latitude=-34.582239,
                        longitude=-58.401159,
                        commune="Comuna 14",
                        neighborhood="Palermo",
                        precision="rooftop",
                    )
                ],
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
            "palermo": GeocodeResult(
                status="ambiguous",
                original_address="Palermo",
                hits=[
                    GeocodeHit(
                        normalized_address="Palermo, CABA (centro aproximado)",
                        latitude=-34.5889,
                        longitude=-58.4306,
                        commune="Comuna 14",
                        neighborhood="Palermo",
                        precision="neighborhood",
                    ),
                    GeocodeHit(
                        normalized_address="Av. Santa Fe y Coronel Diaz, Palermo, CABA",
                        latitude=-34.5865,
                        longitude=-58.4095,
                        commune="Comuna 14",
                        neighborhood="Palermo",
                        precision="intersection",
                    ),
                ],
                message="Hay varias coincidencias. Selecciona la ubicacion correcta.",
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
            "mar del plata": GeocodeResult(
                status="out_of_scope",
                original_address="Mar del Plata",
                hits=[],
                message="La ubicacion parece estar fuera de CABA.",
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
            "cordoba capital": GeocodeResult(
                status="out_of_scope",
                original_address="Cordoba Capital",
                hits=[],
                message="La ubicacion parece estar fuera de CABA.",
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            ),
        }

    async def geocode(self, address: str) -> GeocodeResult:
        key = _normalize_key(address)
        if key in self.FIXTURES:
            result = self.FIXTURES[key]
            return GeocodeResult(
                status=result.status,
                original_address=address,
                hits=list(result.hits),
                message=result.message,
                provider_id=result.provider_id,
                provider_name=result.provider_name,
                retrieved_at=datetime.now(timezone.utc),
            )

        out_of_scope_tokens = ("mar del plata", "rosario", "cordoba", "mendoza", "la plata")
        if any(token in key for token in out_of_scope_tokens):
            return GeocodeResult(
                status="out_of_scope",
                original_address=address,
                message="La ubicacion parece estar fuera de CABA.",
                provider_id="geocoder-mock",
                provider_name="Mock geocoder CABA",
            )

        return GeocodeResult(
            status="not_found",
            original_address=address,
            message="No se pudo geocodificar la direccion.",
            provider_id="geocoder-mock",
            provider_name="Mock geocoder CABA",
        )


class UsigGeocoder(GeocoderClient):
    """USIG / GCBA normalizador + datos utiles (comuna/barrio)."""

    def __init__(
        self,
        base_url: str,
        ws_base_url: str,
        timeout_seconds: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.ws_base_url = ws_base_url.rstrip("/")
        self.timeout = timeout_seconds

    async def geocode(self, address: str) -> GeocodeResult:
        url = f"{self.base_url}/normalizar/?direccion={quote(address)}&geocodificar=true"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

            direcciones = payload.get("direccionesNormalizadas") or []
            if not direcciones:
                return self._result(
                    status="not_found",
                    address=address,
                    message="No se pudo geocodificar la direccion.",
                )

            caba_items = [item for item in direcciones if _is_caba_item(item)]
            if not caba_items:
                return self._result(
                    status="out_of_scope",
                    address=address,
                    message="La ubicacion parece estar fuera de CABA.",
                )

            hits: list[GeocodeHit] = []
            for item in caba_items:
                hit = await self._item_to_hit(client, item, address)
                if hit is not None:
                    hits.append(hit)

            if not hits:
                return self._result(
                    status="not_found",
                    address=address,
                    message="No se pudo geocodificar la direccion.",
                )

            if len(hits) > 1:
                return self._result(
                    status="ambiguous",
                    address=address,
                    hits=hits,
                    message="Hay varias coincidencias en CABA. Selecciona la ubicacion correcta.",
                )

            return self._result(status="confirmed", address=address, hits=hits)

    async def _item_to_hit(
        self,
        client: httpx.AsyncClient,
        item: dict[str, Any],
        fallback_address: str,
    ) -> GeocodeHit | None:
        coords = item.get("coordenadas") or {}
        lat_raw = coords.get("y")
        lon_raw = coords.get("x")
        if lat_raw is None or lon_raw is None:
            return None

        latitude = float(lat_raw)
        longitude = float(lon_raw)
        commune = item.get("nombre_comuna") or item.get("comuna")
        neighborhood = item.get("nombre_barrio") or item.get("barrio")

        if not commune or not neighborhood:
            enriched = await self._lookup_datos_utiles(client, longitude, latitude)
            commune = commune or enriched.get("comuna")
            neighborhood = neighborhood or enriched.get("barrio")

        return GeocodeHit(
            normalized_address=item.get("direccion")
            or item.get("nombre_calle")
            or fallback_address,
            latitude=latitude,
            longitude=longitude,
            commune=commune,
            neighborhood=neighborhood,
            city="Ciudad Autonoma de Buenos Aires",
            precision="rooftop" if item.get("altura") else "street",
        )

    async def _lookup_datos_utiles(
        self,
        client: httpx.AsyncClient,
        longitude: float,
        latitude: float,
    ) -> dict[str, str | None]:
        """Convert WGS84 -> GKBA and resolve comuna/barrio via datos_utiles."""
        try:
            convert = await client.get(
                f"{self.ws_base_url}/rest/convertir_coordenadas",
                params={"x": longitude, "y": latitude, "output": "gkba"},
            )
            convert.raise_for_status()
            resultado = (convert.json() or {}).get("resultado") or {}
            x = resultado.get("x")
            y = resultado.get("y")
            if x is None or y is None:
                return {"comuna": None, "barrio": None}

            useful = await client.get(
                f"{self.ws_base_url}/datos_utiles",
                params={"x": x, "y": y},
            )
            useful.raise_for_status()
            data = useful.json() or {}
            return {
                "comuna": data.get("comuna"),
                "barrio": data.get("barrio"),
            }
        except (httpx.HTTPError, ValueError, TypeError):
            return {"comuna": None, "barrio": None}

    @staticmethod
    def _result(
        *,
        status: GeocodeStatus,
        address: str,
        hits: list[GeocodeHit] | None = None,
        message: str | None = None,
    ) -> GeocodeResult:
        return GeocodeResult(
            status=status,
            original_address=address,
            hits=hits or [],
            message=message,
            provider_id="geocoder-usig",
            provider_name="USIG GCBA",
            retrieved_at=datetime.now(timezone.utc),
        )


def get_geocoder(settings: Settings) -> GeocoderClient:
    provider = (settings.geocoder_provider or "mock").lower()
    if provider == "usig":
        return UsigGeocoder(
            base_url=settings.geocoder_base_url,
            ws_base_url=settings.geocoder_ws_base_url,
            timeout_seconds=settings.geocoder_timeout_seconds,
        )
    return MockGeocoder()
