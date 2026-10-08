# Setup local

## Requisitos

- Python 3.13+
- Docker Desktop (PostgreSQL + PostGIS)

## Arranque rápido (Windows PowerShell)

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

## Variables de entorno relevantes

Copiar desde `.env.example`. Las más usadas:

| Variable | Valores típicos | Efecto |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://tecba:tecba@localhost:5432/tecba` | Postgres local |
| `GEOCODER_PROVIDER` | `mock` / `usig` | Geocoder local vs USIG real |
| `EPOK_PROVIDER` | `epok` / `mock` | Zoning Ciudad 3D vs fixtures |
| `LLM_API_KEY` | vacío o key | Sin key → interpretación mock |
| `LLM_BASE_URL` / `LLM_MODEL` | OpenAI-compatible | Cliente LLM |
| `BA_DATA_*` | URL + User-Agent | Cliente CKAN (scripts / futuro) |

Reiniciar uvicorn después de cambiar `.env`.

## Docker (API + DB)

```powershell
Copy-Item .env.example .env
docker compose --profile full up --build
```

## Postman

1. Importar `postman/InobaLab-TECBA.postman_collection.json`
2. Importar `postman/InobaLab-TECBA.local.postman_environment.json`
3. Seleccionar environment **InobaLab TECBA — local**
4. Empezar por **00 Health → GET Health**

Orden completo: [`../postman/README.md`](../postman/README.md)

Tip: en Windows preferí `http://127.0.0.1:8000` como `baseUrl`.

## Datos y refresh

Ver [snapshots-y-seed.md](snapshots-y-seed.md): `fetch_*` actualiza JSON; `seed` escribe en DB; la API no hace falta para eso.

## Estructura del código

```text
app/
  api/v1/     # routers
  core/       # settings, logging
  schemas/    # contratos Pydantic
  db/         # session, seed, snapshots
  models/     # SQLAlchemy
  services/   # orquestación
  providers/  # USIG, epok, LLM, BA Data
postman/      # colección y environments
scripts/      # regenerar snapshots
documents/    # esta documentación
```
