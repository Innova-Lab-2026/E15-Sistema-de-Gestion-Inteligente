# InobaLab TECBA API

Backend FastAPI del MVP de orientación ciudadana (CABA).

**Documentación de onboarding:** [documents/README.md](documents/README.md)

Ahí están el overview, endpoints, fuentes, snapshots/seed, setup, guía del equipo y el plan por etapas.

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

## Estructura

```text
app/          # API, services, providers, db, models
documents/    # documentación de onboarding
postman/      # colección y environments
scripts/      # regenerar snapshots oficiales
```
