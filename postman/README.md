# Orden de ejecución — colección Postman

Importar (reimportar si ya tenías una versión vieja):

1. `InobaLab-TECBA.postman_collection.json`
2. `InobaLab-TECBA.local.postman_environment.json` (seleccionar environment)

Tip: preferí `http://127.0.0.1:8000` en `baseUrl` si `localhost` da 404 en Windows.

## Etapa 0

1. **00 Health → GET Health** — `{ "status": "ok" }` (200).

## Etapa 1

1. **01 Catalog → GET Activities**
2. **01 Catalog → GET Sources**
3. **01 Catalog → GET Offices** (debe incluir `source_ids`)
4. **01 Catalog → GET Offices by category and commune**

## Etapa 2

1. **02 Location → POST Geocode — Corrientes 2500** → `confirmed` + comuna/barrio
2. **02 Location → POST Geocode — Libertador 1954 CABA** → un solo candidato CABA con comuna/barrio
3. **02 Location → POST Geocode — Palermo ambiguous** → con mock `ambiguous`; con USIG suele ser `not_found` (hace falta calle+altura)
4. **02 Location → POST Geocode — outside CABA** → `out_of_scope` (mock) o `not_found` (USIG)
5. **02 Location → POST Geocode — not found** → `not_found`
6. **02 Location → POST Geocode — empty address** → 422

## Etapa 3 — Consultas

1. **03 Consultations → cafe + Corrientes (deterministic)** → `complete`/`partial` + requirements + sources
2. **03 Consultations → NL query cafeteria** → interpreta `cafe` + geocode + orientación
3. **03 Consultations → actividad invalida** → `activity_unknown`
4. **03 Consultations → fuera de CABA** → `out_of_scope` o `location_not_found`

## Etapa 4 — Interpretación

1. **04 Interpretations → cafeteria Corrientes** → `ready_for_geocoding`, `activity=cafe`
## Etapa 3b — Trámites + zoning + BA Data

1. **01 Catalog → GET Sources (tramites curados)** → `source-005` / `source-006`
2. **01 Catalog → GET Open Data packages (BA Data)** → gastronomia total
3. **01 Catalog → GET Gastronomy context Balvanera** → conteos comuna/barrio
4. **02 Location → POST Zoning** → smp + mixtura
5. **03 Consultations → cafeteria + Corrientes** → 6 pasos + `zoning` + bloque BA Data
3. **04 Interpretations → sin direccion** → `needs_clarification`
4. **04 Interpretations → fuera de catalogo** → `activity_unknown` / `out_of_scope`

Sin `LLM_API_KEY` usa intérprete mock. Con key intenta LLM y, si falla, cae a mock.

Flujo sugerido: Interpret → Geocode, o Consultation NL de un solo paso.

## Próximas etapas

- Etapa 5: folder `05 Partial / Confirmation`
- Etapa 6: folder `06 Follow-ups`
