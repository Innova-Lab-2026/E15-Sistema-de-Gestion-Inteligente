# Endpoints API v1

Base local: `http://127.0.0.1:8000`  
Contrato completo e interactivo: `/docs`  
Orden de prueba: [`../postman/README.md`](../postman/README.md)

Prefijo de negocio: `/api/v1` (salvo health).

## Health

| Método | Path | Body | Respuesta |
|---|---|---|---|
| GET | `/health` | — | `{ "status": "ok" }` (liveness, no toca la base) |
| GET | `/ready` | — | `{ "status": "ready" }` o 503 `database_unavailable` |
| GET | `/status` | — | Proveedores activos sin claves: `llm.active` (`llm` o `rules`) y modelo, `geocoder.simulated` (`true` = geocodificador simulado), `geocoder.breaker_open`, `epok.simulated`, y cuántas filas tiene cada archivo de `data/` |

## Catálogo

| Método | Path | Query / body | Respuesta |
|---|---|---|---|
| GET | `/api/v1/activities` | — | Lista de rubros (`code` = `rubro_{id}` epok) |
| GET | `/api/v1/sources` | — | Fuentes con `validity_status`, URLs |
| GET | `/api/v1/offices` | `category`, `commune` opcionales | Oficinas/canales con `source_ids` |

Ejemplo filtro: `GET /api/v1/offices?category=rubro_16&commune=5` (también acepta `commune=Comuna 5`)

## Ubicación

| Método | Path | Body mínimo | Respuesta |
|---|---|---|---|
| POST | `/api/v1/locations/geocode` | `{ "address": "Av. Corrientes 2500" }` | `confirmed` / `ambiguous` / `out_of_scope` / `not_found` / `unavailable` (USIG caído) + candidatos |
| POST | `/api/v1/locations/zoning` | `{ "latitude": -34.604, "longitude": -58.413, "activity_code": "rubro_102" }` | parcela `smp`, mixtura, `rubro_allowed` |

## Interpretación (NL → actividad + dirección)

| Método | Path | Body mínimo | Respuesta |
|---|---|---|---|
| POST | `/api/v1/interpretations` | `{ "query": "Quiero abrir una cafeteria en Av. Corrientes 2500..." }` | actividad normalizada + candidatos + dirección y barrio + `reason`/`message` |

Sin `LLM_API_KEY` (o si el LLM falla) usa reglas locales (mock). Si el LLM estaba configurado y falló, `fallback_reason` dice por qué (`llm_unavailable`, `llm_rate_limited` o `llm_invalid_output`).

Campos de la respuesta:

| Campo | Qué es |
|---|---|
| `activity` | `raw_text` (palabras literales de la consulta), `normalized_category` (`rubro_{id}` o `null`), `display_name`, `confidence` |
| `activity_candidates` | Hasta 3 `{ code, name, score, match }`, el mejor primero. `match`: `synonym`, `llm` o `name` |
| `location` | `raw_text`, `address` (altura en cifras), `neighborhood_id` (`barrio_id` de `data/barrios.csv`), `neighborhood`, `commune` (`"1"`–`"15"`), `approximate` (entre calles) |
| `missing_fields` | Solo `activity`, `location` (ni dirección ni barrio) o `address` (barrio sin calle) |
| `status` | `ready_for_geocoding`, `needs_clarification`, `activity_unknown`, `out_of_scope` |
| `reason` | `null` si está lista; si no, uno de la tabla de abajo |
| `message` | Texto para la persona según `reason` (plantilla del backend, nunca del LLM, sin códigos internos) |

## Aclaraciones: `reason`

Mismos valores en `/interpretations` y `/consultations`.

| `reason` | Cuándo | Ejemplo |
|---|---|---|
| `activity_missing` | No se nombra ninguna actividad | "quiero abrir un negocio" |
| `activity_not_in_catalog` | La actividad no está en el catálogo o es dudosa: mostrar `activity_candidates` | "tienda de regalos en Florida 500" |
| `location_missing` | Rubro sin dirección ni barrio | "quiero abrir una cafetería" |
| `location_neighborhood_only` | Rubro y barrio, sin calle: consulta `partial` | "peluquería en Belgrano" |
| `location_not_found` | El geocodificador no encuentra la dirección | `address: "Calle Inexistente 123"` |
| `location_ambiguous` | Varias coincidencias: elegir en `location.candidates` | `address: "Palermo"` (mock) |
| `location_outside_caba` | Fuera de CABA | `address: "Mar del Plata"` |
| `topic_out_of_scope` | No es sobre abrir una actividad | "cómo saco el DNI" |

Regla para elegir el rubro sin preguntar: el primer candidato con `score >= 0.85` y al menos 0.1 por encima del segundo. Elegido un candidato, mandar `activity_code` + `address` (o `neighborhood_id`) a `/consultations`.

## Consultas unificadas

| Método | Path | Body | Respuesta |
|---|---|---|---|
| POST | `/api/v1/consultations` | Determinístico: `{ "activity_code": "rubro_102", "address": "Av. Corrientes 2500" }` o `{ "activity_code": "rubro_315", "neighborhood_id": "belgrano" }` **o** NL: `{ "query": "..." }` | Orientación: requirements, offices, zoning, sources, contexto BA Data |

Estados tipados incluyen actividad desconocida, ubicación fuera de CABA, parcial si epok o USIG fallan, etc. Cada estado bloqueado trae `reason` y `message` (ver [Aclaraciones](#aclaraciones-reason)) y la `interpretation` parcial (rubro, dirección, barrio y `activity_candidates` ya detectados). Con rubro y barrio sin calle: `status: "partial"`, `location.status: "neighborhood"`, `reason: "location_neighborhood_only"`, trámites y sede de la comuna sin zonificación. `location.commune` es siempre `"1"`–`"15"` y `location.neighborhood_id` el `barrio_id`.

Warnings posibles en `data_status.warnings`: `epok_unavailable`, `epok_parcel_not_found`, `rubro_not_allowed_in_mixtura`, `ambiguous_address`, `address_approximate` (entre calles: se usó la primera esquina), `no_sources_linked`, `geocoder_unavailable`, `llm_fallback_mock`.

## Open data (snapshot BA Data)

| Método | Path | Query | Respuesta |
|---|---|---|---|
| GET | `/api/v1/open-data/packages` | — | Metadatos CKAN del snapshot local |
| GET | `/api/v1/open-data/gastronomy-context` | `commune`, `neighborhood` | Conteos de oferta gastronómica |

Ejemplo: `GET /api/v1/open-data/gastronomy-context?commune=3&neighborhood=Balvanera`

## Errores, límites y rate limit

Todo error usa `{ "error": { code, message, detail, request_id } }` y cada respuesta lleva `X-Request-ID`. `/consultations`, `/interpretations` y `/locations/*` tienen rate limit por IP (429 `rate_limited` + `Retry-After`) y límites de largo y coordenadas. Detalle: [errores-y-seguridad.md](errores-y-seguridad.md).

## Notas

- Preferí `127.0.0.1` en Windows si `localhost` da problemas.
- Tras cambiar `.env` (geocoder/epok/LLM), reiniciar uvicorn.
