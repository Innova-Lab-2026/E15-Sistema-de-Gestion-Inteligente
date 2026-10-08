"""Cliente Ciudad 3D / epok: parcela, mixtura, rubros y referencias."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

import httpx

from app.core.config import Settings
from app.db.catalog_data import load_epok_rubros


ZoningStatus = Literal[
    "ok",
    "parcel_not_found",
    "unavailable",
    "rubro_allowed",
    "rubro_not_allowed",
]


@dataclass
class ParcelData:
    smp: str
    direccion: str | None = None
    seccion: str | None = None
    manzana: str | None = None
    parcela: str | None = None
    superficie_total: str | None = None
    centroide: list[float] | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ZoningResult:
    status: ZoningStatus
    latitude: float
    longitude: float
    parcel: ParcelData | None = None
    mixtura: int | None = None
    usos: list[int] = field(default_factory=list)
    affectations: dict[str, Any] | None = None
    epok_category_id: int | None = None
    epok_rubro_id: int | None = None
    rubro_allowed: bool | None = None
    allowed_rubro_ids: list[int] = field(default_factory=list)
    referencias: dict[str, Any] | None = None
    message: str | None = None
    provider_id: str = "epok"
    provider_name: str = "Ciudad 3D / epok"
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EpokClient(ABC):
    @abstractmethod
    async def lookup_zoning(
        self,
        *,
        latitude: float,
        longitude: float,
        epok_category_id: int | None = None,
        epok_rubro_id: int | None = None,
    ) -> ZoningResult:
        raise NotImplementedError


def _parse_mixtura(usos: list[Any]) -> int | None:
    """Ciudad 3D devuelve p.ej. usos:[4,0,0] → mixtura 4."""
    for value in usos:
        try:
            n = int(value)
        except (TypeError, ValueError):
            continue
        if n > 0:
            return n
    return None


def _rubro_allowed_from_snapshot(
    *,
    epok_rubro_id: int,
    epok_category_id: int | None,
    mixtura: int,
) -> tuple[bool, list[int]]:
    allowed_ids: list[int] = []
    target_ok = False
    for item in load_epok_rubros():
        rid = int(item["rubro_id"])
        cat = int(item["categoria_id"])
        mixturas = [int(m) for m in item.get("mixturas", [])]
        if mixtura not in mixturas:
            continue
        if epok_category_id is not None and cat != epok_category_id:
            continue
        allowed_ids.append(rid)
        if rid == epok_rubro_id:
            target_ok = True
    return target_ok, sorted(allowed_ids)


class MockEpokClient(EpokClient):
    """Fixtures locales para Corrientes / coords tipicas del mock geocoder."""

    def __init__(self) -> None:
        self._parcels: dict[tuple[float, float], ParcelData] = {
            (-34.604, -58.413): ParcelData(
                smp="013-051-005F",
                direccion="CORRIENTES AV. 3399",
                seccion="013",
                manzana="051",
                parcela="005F",
                superficie_total="246.00",
                centroide=[-58.412949, -34.60396],
            ),
            (-34.604, -58.4035): ParcelData(
                smp="009-020-015",
                direccion="PASO 441",
                seccion="009",
                manzana="020",
                parcela="015",
                superficie_total="249.00",
                centroide=[-58.403381, -34.603981],
            ),
        }

    def _nearest_parcel(self, latitude: float, longitude: float) -> ParcelData | None:
        best: ParcelData | None = None
        best_d = 1e9
        for (lat, lng), parcel in self._parcels.items():
            d = abs(lat - latitude) + abs(lng - longitude)
            if d < best_d:
                best_d = d
                best = parcel
        # tolerancia ~3 cuadras aprox
        if best is not None and best_d < 0.02:
            return best
        return None

    async def lookup_zoning(
        self,
        *,
        latitude: float,
        longitude: float,
        epok_category_id: int | None = None,
        epok_rubro_id: int | None = None,
    ) -> ZoningResult:
        parcel = self._nearest_parcel(latitude, longitude)
        if parcel is None:
            return ZoningResult(
                status="parcel_not_found",
                latitude=latitude,
                longitude=longitude,
                message="Mock epok: no hay parcela fixture cerca de esas coordenadas.",
                provider_id="epok-mock",
                provider_name="Mock Ciudad 3D / epok",
            )
        mixtura = 4
        usos = [4, 0, 0]
        affectations = {
            "riesgo_hidrico": 0,
            "lep": 0,
            "ensanche": 0,
            "apertura": 0,
            "ci_digital": 0,
        }
        rubro_allowed: bool | None = None
        allowed_ids: list[int] = []
        status: ZoningStatus = "ok"
        message = f"Parcela {parcel.smp}, mixtura {mixtura} (mock)."
        if epok_rubro_id is not None:
            rubro_allowed, allowed_ids = _rubro_allowed_from_snapshot(
                epok_rubro_id=epok_rubro_id,
                epok_category_id=epok_category_id,
                mixtura=mixtura,
            )
            status = "rubro_allowed" if rubro_allowed else "rubro_not_allowed"
            message = (
                f"Rubro {epok_rubro_id} "
                f"{'permitido' if rubro_allowed else 'NO permitido'} "
                f"en mixtura {mixtura} (mock / snapshot local)."
            )
        return ZoningResult(
            status=status,
            latitude=latitude,
            longitude=longitude,
            parcel=parcel,
            mixtura=mixtura,
            usos=usos,
            affectations=affectations,
            epok_category_id=epok_category_id,
            epok_rubro_id=epok_rubro_id,
            rubro_allowed=rubro_allowed,
            allowed_rubro_ids=allowed_ids[:50],
            message=message,
            provider_id="epok-mock",
            provider_name="Mock Ciudad 3D / epok",
        )


class HttpEpokClient(EpokClient):
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.epok_base_url.rstrip("/")
        self.timeout = settings.epok_timeout_seconds

    async def lookup_zoning(
        self,
        *,
        latitude: float,
        longitude: float,
        epok_category_id: int | None = None,
        epok_rubro_id: int | None = None,
    ) -> ZoningResult:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                parcel = await self._fetch_parcel(client, latitude, longitude)
                if parcel is None:
                    return ZoningResult(
                        status="parcel_not_found",
                        latitude=latitude,
                        longitude=longitude,
                        epok_category_id=epok_category_id,
                        epok_rubro_id=epok_rubro_id,
                        message="epok no devolvio parcela para esas coordenadas.",
                    )

                usos_raw = await self._get_json(
                    client, "/cur3d/mixtura_usos/", params={"smp": parcel.smp}
                )
                usos = [int(x) for x in (usos_raw or {}).get("usos", []) if str(x).isdigit() or isinstance(x, int)]
                mixtura = _parse_mixtura(usos)

                affectations = await self._get_json(
                    client, "/cur3d/afectaciones/", params={"smp": parcel.smp}
                )

                rubro_allowed: bool | None = None
                allowed_ids: list[int] = []
                referencias: dict[str, Any] | None = None
                status: ZoningStatus = "ok"
                message = f"Parcela {parcel.smp}"
                if mixtura is not None:
                    message += f", mixtura {mixtura}"
                else:
                    message += ", mixtura no determinada"

                if epok_rubro_id is not None and mixtura is not None:
                    if epok_category_id is not None:
                        rubros_data = await self._get_json(
                            client,
                            "/cur3d/cuadrosdeuso/rubros/",
                            params={
                                "categoria": epok_category_id,
                                "mixtura": mixtura,
                            },
                        )
                        allowed_ids = [
                            int(r["rubro_id"])
                            for r in (rubros_data or {}).get("rubros", [])
                            if "rubro_id" in r
                        ]
                        rubro_allowed = epok_rubro_id in allowed_ids
                    else:
                        rubro_allowed, allowed_ids = _rubro_allowed_from_snapshot(
                            epok_rubro_id=epok_rubro_id,
                            epok_category_id=None,
                            mixtura=mixtura,
                        )

                    if rubro_allowed and epok_category_id is not None:
                        referencias = await self._get_json(
                            client,
                            "/cur3d/cuadrosdeuso/referencias/",
                            params={
                                "categoria": epok_category_id,
                                "mixtura": mixtura,
                                "rubro": epok_rubro_id,
                            },
                        )

                    status = "rubro_allowed" if rubro_allowed else "rubro_not_allowed"
                    message = (
                        f"Rubro {epok_rubro_id} "
                        f"{'permitido' if rubro_allowed else 'NO permitido'} "
                        f"en parcela {parcel.smp} (mixtura {mixtura})."
                    )

                return ZoningResult(
                    status=status,
                    latitude=latitude,
                    longitude=longitude,
                    parcel=parcel,
                    mixtura=mixtura,
                    usos=usos,
                    affectations=affectations if isinstance(affectations, dict) else None,
                    epok_category_id=epok_category_id,
                    epok_rubro_id=epok_rubro_id,
                    rubro_allowed=rubro_allowed,
                    allowed_rubro_ids=allowed_ids[:50],
                    referencias=referencias,
                    message=message,
                )
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            return ZoningResult(
                status="unavailable",
                latitude=latitude,
                longitude=longitude,
                epok_category_id=epok_category_id,
                epok_rubro_id=epok_rubro_id,
                message=f"epok no disponible: {exc}",
            )

    async def _fetch_parcel(
        self, client: httpx.AsyncClient, latitude: float, longitude: float
    ) -> ParcelData | None:
        # Algunas coords de USIG caen en via / hueco; probar offsets cortos (~15-40 m).
        offsets = [
            (0.0, 0.0),
            (0.00015, 0.0),
            (-0.00015, 0.0),
            (0.0, 0.00015),
            (0.0, -0.00015),
            (0.0003, 0.0003),
            (-0.0003, -0.0003),
            (0.0003, -0.0003),
            (-0.0003, 0.0003),
        ]
        for dlat, dlng in offsets:
            data = await self._get_json(
                client,
                "/catastro/parcela/",
                params={"lng": longitude + dlng, "lat": latitude + dlat},
            )
            if data and data.get("smp"):
                return ParcelData(
                    smp=str(data["smp"]),
                    direccion=data.get("direccion"),
                    seccion=str(data["seccion"]) if data.get("seccion") is not None else None,
                    manzana=str(data["manzana"]) if data.get("manzana") is not None else None,
                    parcela=str(data["parcela"]) if data.get("parcela") is not None else None,
                    superficie_total=(
                        str(data["superficie_total"])
                        if data.get("superficie_total") is not None
                        else None
                    ),
                    centroide=data.get("centroide")
                    if isinstance(data.get("centroide"), list)
                    else None,
                    raw=data,
                )
        return None

    async def _get_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        url = f"{self.base_url}{path}"
        response = await client.get(url, params=params)
        response.raise_for_status()
        if not response.content:
            return None
        data = response.json()
        if data == {} or data is None:
            return None
        if isinstance(data, dict):
            return data
        return None


def get_epok_client(settings: Settings) -> EpokClient:
    provider = (settings.epok_provider or "epok").strip().lower()
    if provider == "mock":
        return MockEpokClient()
    return HttpEpokClient(settings)
