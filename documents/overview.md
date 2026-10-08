# Overview del producto (API)

## Qué resuelve

Una persona quiere iniciar una actividad económica en CABA (por ejemplo, abrir una cafetería en Av. Corrientes 2500). La información oficial está dispersa: geocodificación, normativa del lote, trámites de habilitación, oficinas de atención.

Este API arma una **respuesta de orientación** unificada: actividad, ubicación, zoning (epok), requisitos curados, oficinas reales y fuentes trazables.

## Flujo típico de una consulta

```text
query NL  ──► interpretación (LLM o mock)
                    │
activity_code + address
                    │
                    ▼
              geocode USIG  ──► lat/lng, comuna, barrio
                    │
                    ▼
         zoning epok (parcela/smp/mixtura/rubro)
                    │
                    ▼
   requirements + offices + BA Data context + sources
                    │
                    ▼
            ConsultationResponse
```

También se puede llamar en modo **determinístico** (sin NL): `activity_code` + `address` directo a `POST /api/v1/consultations`.

## Capas del repo

| Capa | Rol |
|---|---|
| `app/api/v1/` | Routers HTTP |
| `app/schemas/` | Contratos Pydantic |
| `app/services/` | Orquestación (consultation, location, zoning, interpretation) |
| `app/providers/` | Clientes externos (USIG, epok, LLM, BA Data) |
| `app/db/` | Seed, snapshots JSON, sesión SQLAlchemy |
| `app/models/` | Tablas (actividades, oficinas, fuentes, requisitos, capas) |
| `postman/` | Colección de prueba por etapas |
| `scripts/` | Regenerar snapshots oficiales |

## Qué es real vs local

- **Reales (en runtime o snapshot oficial):** USIG, epok, rubros epok, trámites curados GCBA, oficinas AGC/Sedes Comunales, BA Data (snapshot CKAN).
- **Locales / fallback:** mock geocoder, mock epok, mock interpreter si no hay `LLM_API_KEY`.

Detalle de fuentes: [fuentes-y-datos.md](fuentes-y-datos.md).  
Cómo cargar datos: [snapshots-y-seed.md](snapshots-y-seed.md).
