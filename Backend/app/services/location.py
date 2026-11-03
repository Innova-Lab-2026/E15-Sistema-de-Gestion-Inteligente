from app.core.config import Settings, get_settings
from app.providers.geocoder import GeocodeResult, get_geocoder
from app.schemas.location import (
    GeocodeResponse,
    GeocodeSource,
    LocationCandidate,
)


class LocationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.geocoder = get_geocoder(self.settings)

    async def geocode(self, address: str) -> GeocodeResponse:
        cleaned = address.strip()
        result: GeocodeResult = await self.geocoder.geocode(cleaned)
        source = GeocodeSource(
            id=result.provider_id,
            name=result.provider_name,
            retrieved_at=result.retrieved_at,
        )
        candidates = [
            LocationCandidate(
                normalized_address=hit.normalized_address,
                city=hit.city,
                commune=hit.commune,
                neighborhood=hit.neighborhood,
                latitude=hit.latitude,
                longitude=hit.longitude,
                precision=hit.precision,
            )
            for hit in result.hits
        ]

        primary = result.hits[0] if result.hits and result.status == "confirmed" else None
        return GeocodeResponse(
            status=result.status,
            original_address=cleaned,
            normalized_address=primary.normalized_address if primary else None,
            city=primary.city if primary else None,
            commune=primary.commune if primary else None,
            neighborhood=primary.neighborhood if primary else None,
            latitude=primary.latitude if primary else None,
            longitude=primary.longitude if primary else None,
            precision=primary.precision if primary else None,
            candidates=candidates,
            source=source,
            message=result.message,
        )
