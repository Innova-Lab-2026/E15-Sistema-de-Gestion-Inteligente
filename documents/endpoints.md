# Endpoints API v1

Base local: `http://127.0.0.1:8000`  
Contrato completo e interactivo: `/docs`  
Orden de prueba: [`../postman/README.md`](../postman/README.md)

Prefijo de negocio: `/api/v1` (salvo health).

## Health

| Método | Path | Body | Respuesta |
|---|---|---|---|
| GET | `/health` | — | `{ "status": "ok" }` |

## Catálogo

| Método | Path | Query / body | Respuesta |
|---|---|---|---|
| GET | `/api/v1/activities` | — | Lista de rubros (`code` = `rubro_{id}` epok) |
| GET | `/api/v1/sources` | — | Fuentes con `validity_status`, URLs |
| GET | `/api/v1/offices` | `category`, `commune` opcionales | Oficinas/canales con `source_ids` |

Ejemplo filtro: `GET /api/v1/offices?category=rubro_16&commune=5`

## Ubicación

| Método | Path | Body mínimo | Respuesta |
|---|---|---|---|
| POST | `/api/v1/locations/geocode` | `{ "address": "Av. Corrientes 2500" }` | `confirmed` / `ambiguous` / `out_of_scope` / `not_found` + candidatos |
| POST | `/api/v1/locations/zoning` | `{ "latitude": -34.604, "longitude": -58.413, "activity_code": "rubro_102" }` | parcela `smp`, mixtura, `rubro_allowed` |

## Interpretación (NL → actividad + dirección)

| Método | Path | Body mínimo | Respuesta |
|---|---|---|---|
| POST | `/api/v1/interpretations` | `{ "query": "Quiero abrir una cafeteria en Av. Corrientes 2500..." }` | actividad normalizada + dirección candidata |

Sin `LLM_API_KEY` (o si el LLM falla) usa reglas locales (mock).

## Consultas unificadas

| Método | Path | Body | Respuesta |
|---|---|---|---|
| POST | `/api/v1/consultations` | Determinístico: `{ "activity_code": "rubro_102", "address": "Av. Corrientes 2500" }` **o** NL: `{ "query": "..." }` | Orientación: requirements, offices, zoning, sources, contexto BA Data |

Estados tipados incluyen actividad desconocida, ubicación fuera de CABA, parcial si epok falla, etc.

## Open data (snapshot BA Data)

| Método | Path | Query | Respuesta |
|---|---|---|---|
| GET | `/api/v1/open-data/packages` | — | Metadatos CKAN del snapshot local |
| GET | `/api/v1/open-data/gastronomy-context` | `commune`, `neighborhood` | Conteos de oferta gastronómica |

Ejemplo: `GET /api/v1/open-data/gastronomy-context?commune=3&neighborhood=Balvanera`

## Notas

- Preferí `127.0.0.1` en Windows si `localhost` da problemas.
- Tras cambiar `.env` (geocoder/epok/LLM), reiniciar uvicorn.
