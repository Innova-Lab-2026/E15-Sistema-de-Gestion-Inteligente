# InobaLab TECBA API

Backend FastAPI del MVP de orientación ciudadana (CABA).

**Documentación de onboarding:** [documents/README.md](documents/README.md)

Ahí están el overview, endpoints, fuentes, snapshots/seed, setup, guía del equipo y el plan por etapas.

## Qué hace

- Interpreta la consulta en español (LLM con respaldo, o reglas locales sin IA): rubro, dirección (alturas en palabras, esquinas) y barrio.
- Contrato fijo para el Frontend: `reason`, `missing_fields`, `message` de plantilla y hasta 3 `activity_candidates` cuando el rubro es dudoso. Nada de lo que escribe el LLM llega a la respuesta.
- Geocodifica con USIG (con caché y corte si falla), consulta la zonificación en Ciudad 3D / epok y arma requisitos, oficinas y fuentes citadas.
- Con rubro y barrio sin calle responde `partial` con trámites y sede comunal.
- Guarda cada consulta (`GET /api/v1/consultations/{id}`) y las actividades no reconocidas para Data.
- `GET /status`: qué proveedores están activos (real o simulado), sin claves.

Contrato: [documents/endpoints.md](documents/endpoints.md). Datos del equipo de Data: [documents/actualizar-data.md](documents/actualizar-data.md).

## Requisitos

- Python 3.13+
- Docker Desktop (PostgreSQL + PostGIS)

## Setup local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d db
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Detalle de env, providers y refresh de datos: [documents/setup.md](documents/setup.md) y [documents/snapshots-y-seed.md](documents/snapshots-y-seed.md).

## Postman

1. Importar `postman/InobaLab-TECBA.postman_collection.json`
2. Importar `postman/InobaLab-TECBA.local.postman_environment.json`
3. Seleccionar environment **InobaLab TECBA — local**
4. Ejecutar **00 Health → GET Health**

Orden completo: [postman/README.md](postman/README.md)

## Docker (API + DB)

```powershell
Copy-Item .env.example .env
docker compose --profile full up --build
```

El contenedor aplica las migraciones al arrancar.

## Tests

```bash
DB_PORT=5432 scripts/test.sh
```

pytest dentro de la imagen de la API contra la base aislada `tecba_test`. Errores, límites y seguridad: [documents/errores-y-seguridad.md](documents/errores-y-seguridad.md).

## Estructura

```text
app/          # API, services, providers, db, models
data/         # archivos del equipo de Data (barrios, sinónimos, consultas de prueba)
documents/    # documentación de onboarding
postman/      # colección y environments
scripts/      # snapshots oficiales, tests, export para Data, entrypoint Docker
tests/        # pytest (contrato, intérprete, data/, fuentes caídas, punta a punta)
```
