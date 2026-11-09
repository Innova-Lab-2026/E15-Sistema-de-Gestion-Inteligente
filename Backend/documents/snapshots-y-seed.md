# Snapshots, seed y API

## Idea clave

**No hace falta tener uvicorn (la API HTTP) levantada** para refrescar datos.  
Sí hace falta **Postgres** para el seed.

```text
scripts/fetch_*.py  -->  app/db/*_snapshot.json  -->  python -m app.db.seed  -->  Postgres
                                                                              |
                                                                         uvicorn lee DB
```

| Paso | Qué hace | Requiere |
|---|---|---|
| `python scripts/fetch_offices.py` | Baja oficinas oficiales (BA Data + AGC) y geocodifica con USIG → `offices_snapshot.json` | Red |
| `python scripts/fetch_ba_data.py` | Snapshot CKAN / gastronomía → `ba_data_snapshot.json` | Red |
| `python scripts/fetch_epok_rubros.py` | Rubros oficiales → `epok_rubros_snapshot.json` | Red |
| `python -m app.db.seed` | Upsert catálogo, requisitos, oficinas, capas en DB | **DB** (`docker compose up -d db`) |
| `uvicorn app.main:app --reload --port 8000` | Sirve lo ya cargado | DB + proceso API |

## Setup inicial (una vez)

```powershell
docker compose up -d db
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

Los snapshots del repo ya vienen versionados; el seed los usa sin volver a hacer fetch.

## Cuándo regenerar

- Cambió una sede comunal o datos de AGC → `fetch_offices.py` + `seed`
- Actualizar oferta gastronómica / packages BA Data → `fetch_ba_data.py` + `seed`
- Cambió el listado de rubros epok → `fetch_epok_rubros.py` + `seed`

Después del seed, si la API ya estaba corriendo, los endpoints leen la DB actualizada (sin rebuild). Si usás workers con cache en memoria, reiniciá uvicorn por las dudas.

## Oficinas en el seed

- `office-001` — AGC Habilitaciones (Perón 2941)
- `office-002` — canal online SSIT / habilitación
- `office-sede-01` … — sedes y subsedes comunales (BA Data)

Fuente de trazabilidad: `source-003` (AGC + Sedes Comunales).

## Archivos

| Archivo | Rol |
|---|---|
| `app/db/offices_snapshot.json` | Oficinas oficiales |
| `app/db/offices_data.py` | Loader para seed |
| `app/db/ba_data_snapshot.json` | BA Data ETL |
| `app/db/epok_rubros_snapshot.json` | Rubros / catálogo |
| `app/db/seed.py` | Sync a Postgres |
| `scripts/fetch_*.py` | Regenerar snapshots |
