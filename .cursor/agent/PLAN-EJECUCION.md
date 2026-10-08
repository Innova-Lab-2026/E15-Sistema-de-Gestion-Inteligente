# Plan de ejecución del agente — API TECBA

Carpeta del agente: `.cursor/agent/`.  
Plan canónico del equipo: [`documents/plan-implementacion.md`](../../documents/plan-implementacion.md).

Usar este archivo para marcar avance, notas y bloqueos. No duplicar el diseño completo acá; solo ejecución.

---

## Estado general

| Campo | Valor |
|---|---|
| Etapa actual | `5` (siguiente; 3b completa) |
| Última actualización | 2026-10-08 |
| Bloqueadores | ninguno |

---

## Checklist por etapa

### Etapa 0 — Scaffold y entorno

- [x] Estructura `app/` + FastAPI
- [x] Settings / `.env.example`
- [x] Docker Compose PostGIS
- [x] `GET /health`
- [x] Postman: folder `00 Health` + environment `local`
- [x] Criterio: Health → 200

**Notas:** API local en `127.0.0.1:8000`. Contenedor `tecba-db` (PostGIS 16) healthy en puerto 5432. venv en `.venv/`.

### Etapa 1 — Catálogo, modelos y seeds

- [x] Modelos SQLAlchemy + Alembic
- [x] Seed: 3 actividades, 3 fuentes, requisitos, oficinas
- [x] `GET /api/v1/activities`
- [x] `GET /api/v1/sources`
- [x] `GET /api/v1/offices`
- [x] Postman: folder `01 Catalog`
- [x] Criterio: listados con `source_ids`

**Notas:** Migración `001_initial_catalog` + `002_epok_catalog` + `003_epok_rubro_id`. Catalogo = rubros oficiales Ciudad 3D/epok (~401) con `epok_rubro_id`. Sync: `python -m app.db.seed` (snapshot `app/db/epok_rubros_snapshot.json`). Oficinas oficiales: AGC Perón 2941 + SSIT online + Sedes Comunales BA Data (`offices_snapshot.json`; regenerar `python scripts/fetch_offices.py`).

### Etapa 2 — Geocodificación

- [x] `GeocoderClient` USIG + `MockGeocoder`
- [x] `POST /api/v1/locations/geocode`
- [x] Estados: confirmed / ambiguous / out_of_scope / not_found
- [x] Postman: folder `02 Location`
- [x] Criterio: Corrientes 2500 + fuera CABA

**Notas:** `GEOCODER_PROVIDER=mock` por defecto; `usig` en `.env` local. Corrientes 2500 → confirmed; Libertador filtra AMBA y completa comuna/barrio via `datos_utiles`. USIG: `GEOCODER_BASE_URL` + `GEOCODER_WS_BASE_URL`.

### Etapa 3 — Consultation determinística

- [x] `POST /api/v1/consultations` (activity_code + address)
- [x] Pipeline: catálogo → geocode → retrieval → respuesta §11
- [x] Errores tipados (actividad / ubicación)
- [x] Postman: folder `03 Consultations`
- [x] Criterio: requirements + offices + sources

**Notas:** Acepta también `query` NL (usa interpretación). Si LLM falla, cae a mock. Etapa 3b: consultations incluyen `zoning` (smp/mixtura/rubro via epok).

### Etapa 3b — Fuentes reales (epok zoning)

- [x] Cliente epok (`parcela` → `smp` → `mixtura_usos` → rubros/referencias)
- [x] `POST /api/v1/locations/zoning`
- [x] Integración en `POST /consultations` (`zoning` + territorial)
- [x] Estados parciales si epok falla / parcela no encontrada
- [x] Postman: zoning + consultation con smp
- [x] Trámites curados reales (Persona C) — guia GCBA local comercial + URLs
- [x] BA Data ETL básico — snapshot CKAN + oferta gastronomica + open-data API

**Notas:** `EPOK_PROVIDER=epok|mock`. Snapshot rubros + `ba_data_snapshot.json`. Tramites curados. BA Data: `GET /open-data/packages` y `/gastronomy-context`; capas map_layers desde GeoJSON oficiales. Regenerar: `python scripts/fetch_ba_data.py`.

### Etapa 4 — IA interpretación

- [x] `LLMClient` OpenAI-compatible
- [x] `POST /api/v1/interpretations`
- [x] Consultations acepta `query` NL
- [x] Fallback `llm_unavailable` → mock (no bloquea)
- [x] Postman: folder `04 Interpretations`
- [x] Criterio: caso emblemático → rubro_102 / rubro_16 + dirección

**Notas:** Sin `LLM_API_KEY` usa mock. Con key intenta LLM; si falla (ej. URL Gemini), fallback a mock.

### Etapa 5 — IA explicación

- [ ] Servicio `explain` solo con contexto recuperado
- [ ] Campos summary / steps / documents / territorial / map_layers
- [ ] `confirmed_location` + data_status parcial
- [ ] Postman: folder `05 Partial / Confirmation`
- [ ] Criterio: sin inventar requisitos

**Notas:** —

### Etapa 6 — Follow-ups y endurecimiento

- [ ] `POST /api/v1/consultations/{id}/follow-ups`
- [ ] Persistencia Consultation + trazabilidad
- [ ] Timeouts / rate limit / sanitizar URLs
- [ ] pytest e2e
- [ ] Postman: folder `06 Follow-ups` + README orden de colección
- [ ] Criterio: e2e NL + follow-up en contexto

**Notas:** —

---

## Log de ejecución

| Fecha | Etapa | Acción | Resultado |
|---|---|---|---|
| 2026-09-21 | — | Carpeta agente + plan creado | OK |
| 2026-09-21 | 0 | Scaffold FastAPI, Docker PostGIS, `/health`, Postman `00 Health` | OK · Health 200 · db healthy |
| 2026-09-21 | 1 | Modelos, Alembic `001_initial_catalog`, seed MVP, GET catalog | OK · 3 activities · offices con source_ids |
| 2026-09-21 | 2 | MockGeocoder + UsigGeocoder, `POST /locations/geocode`, Postman `02 Location` | OK · confirmed / ambiguous / out_of_scope / 422 |
| 2026-09-21 | 2 | USIG: filtro CABA + enrich comuna/barrio (`datos_utiles`) | OK · Libertador → Comuna 14 Palermo |
| 2026-09-30 | 4 | `POST /interpretations` + LLM client + mock local + Postman `04` | OK · cafe/Corrientes ready_for_geocoding |
| 2026-09-30 | 3 | `POST /consultations` determinístico + NL + Postman `03` | OK · complete cafe + Comuna 3 + requirements |
| 2026-09-30 | cat | Catalogo medio epok: 30 actividades + `epok_category_*` + sync seed | OK · ferreteria → hardware_store |
| 2026-09-30 | cat | Codes del catalogo renombrados a español | OK · cafe→cafeteria, hardware_store→ferreteria, etc. |
| 2026-09-30 | cat | Catalogo = rubros oficiales epok (401) + `epok_rubro_id` | OK · code `rubro_{id}` · snapshot + aliases NL |
| 2026-09-30 | 3b | Cliente epok + `/locations/zoning` + consultations.zoning | OK · smp/mixtura/rubro_allowed |
| 2026-09-30 | 3b | Tramites GCBA curados + sources 005-007 + url_fuente | OK · guia 6 pasos en rubro_102 |
| 2026-09-30 | 3b | BA Data ETL + `/open-data/*` + contexto en consultations | OK · 2823 locales · Balvanera 215 |
| 2026-10-08 | 1/3b | Oficinas oficiales: AGC + SSIT + 21 sedes BA Data | OK · `offices_snapshot.json` · USIG coords |

---

## Convención

1. Leer [`documents/plan-implementacion.md`](../../documents/plan-implementacion.md) antes de implementar.
2. Ejecutar **una etapa a la vez**.
3. Actualizar checklist + log en este archivo al cerrar cada etapa.
4. Toda etapa con endpoint nuevo actualiza `postman/` en el mismo cambio.
