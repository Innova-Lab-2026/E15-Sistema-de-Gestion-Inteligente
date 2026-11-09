# Fuentes y datos

Mapa de fuentes oficiales que usa el MVP. Pruebas de acceso detalladas: [fuentes-pruebas.md](fuentes-pruebas.md).

## Resumen

| Fuente | Qué aporta | Cómo entra al API |
|---|---|---|
| **USIG** | Normaliza dirección → lat/lng, comuna, barrio | Runtime: `GEOCODER_PROVIDER=usig` |
| **Ciudad 3D / epok** | Parcela (`smp`), mixtura, rubros permitidos | Runtime: `EPOK_PROVIDER=epok` + catálogo desde snapshot |
| **Trámites GCBA** | Pasos/requisitos de habilitación comercial | Curado en `app/db/tramites_curados.py` (sin API oficial) |
| **BA Data (CKAN)** | Datasets abiertos (gastronomía, comunas, barrios, sedes) | Snapshot ETL + endpoints `/open-data/*` |
| **AGC + Sedes Comunales** | Oficinas reales de atención | Snapshot `offices_snapshot.json` → seed |

## USIG (geocoder)

- Endpoint interno del proyecto: `POST /api/v1/locations/geocode`
- Provider: `app/providers/geocoder.py`
- Offline / tests: `GEOCODER_PROVIDER=mock`

## epok (zoning + rubros)

- Zoning: `POST /api/v1/locations/zoning` y bloque `zoning` en consultations
- Catálogo de actividades = rubros oficiales (`code` = `rubro_{id}`) desde `app/db/epok_rubros_snapshot.json`
- Regenerar catálogo: `python scripts/fetch_epok_rubros.py` → luego seed

## Trámites curados

- Guía comercial GCBA + URLs de habilitación / exprés
- Seed crea `Requirement` + `Source` (`source-001`, `source-005`, `source-006`, …) con `url_fuente`
- No se inventan requisitos: solo lo curado

## BA Data

- Snapshot: `app/db/ba_data_snapshot.json`
- Regenerar: `python scripts/fetch_ba_data.py`
- Endpoints: `GET /api/v1/open-data/packages`, `.../gastronomy-context`
- En consultations: contexto de oferta gastronómica por comuna/barrio cuando aplica

## Oficinas oficiales

| Tipo | Ejemplo | Origen |
|---|---|---|
| Física AGC | Tte. Juan Domingo Perón 2941 | Trámite habilitación GCBA |
| Online | SSIT / miBA | Misma URL oficial |
| Sedes / subsedes comunales | 21 puntos BA Data | Dataset Sedes Comunales + coords USIG |

Snapshot: `app/db/offices_snapshot.json`  
Regenerar: `python scripts/fetch_offices.py` → `python -m app.db.seed`  
Detalle operativo: [snapshots-y-seed.md](snapshots-y-seed.md).
