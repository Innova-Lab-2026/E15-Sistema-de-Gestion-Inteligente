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

- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) · Ready (DB): [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Variables de entorno relevantes

Copiar desde `.env.example`. Las más usadas:

| Variable | Valores típicos | Efecto |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://tecba:tecba@localhost:5432/tecba` | Postgres local |
| `APP_ENV` | `local` / `production` (default) | `local` sincroniza el catálogo al arrancar; en otro entorno el seed es explícito |
| `GEOCODER_PROVIDER` | `usig` (default) / `mock` | USIG real vs fixtures locales (solo offline/tests) |
| `EPOK_PROVIDER` | `epok` / `mock` | Zoning Ciudad 3D vs fixtures |
| `LLM_API_KEY` | vacío o key | Sin key → interpretación mock |
| `LLM_BASE_URL` / `LLM_MODEL` | OpenAI-compatible | Cliente LLM |
| `BA_DATA_*` | URL + User-Agent | Cliente CKAN (scripts / futuro) |
| `DEBUG` | `false` / `true` | `true` loguea las queries SQL |
| `CORS_ORIGINS` / `CORS_ALLOW_CREDENTIALS` | lista separada por comas / `false` | Orígenes del frontend (incluye Vite `:5173` por defecto) |
| `HTTP_USER_AGENT` / `HTTP_TIMEOUT_SECONDS` / `HTTP_RETRIES` | — | Cliente HTTP compartido para USIG y epok |
| `RATE_LIMIT_ENABLED` / `RATE_LIMIT_PER_MINUTE` | `true` / `30` | Límite por IP en rutas que llaman al LLM, USIG o epok |
| `MAX_REQUEST_BYTES` | `65536` | Bodies más grandes → 413 |
| `RUN_MIGRATIONS` / `RUN_SEED` | `true` / `false` | Entrypoint de Docker |

Detalle de errores, límites y defaults seguros: [errores-y-seguridad.md](errores-y-seguridad.md).

Reiniciar uvicorn después de cambiar `.env`.

## Docker (API + DB)

```powershell
Copy-Item .env.example .env
docker compose --profile full up --build
```

El contenedor corre `alembic upgrade head` al arrancar (`RUN_MIGRATIONS=true`). Con `APP_ENV=local` (el valor de `.env.example`) la API además sincroniza el catálogo; en otro entorno usar `RUN_SEED=true` o `python -m app.db.seed`. Puertos del host configurables: `DB_PORT=5433 API_PORT=8001 docker compose --profile full up`.

## Tests

Requieren el Postgres del compose levantado (`docker compose up -d db`) y la imagen de la API construida.

```bash
DB_PORT=5432 scripts/test.sh           # todos
DB_PORT=5432 scripts/test.sh -k golden # solo las respuestas de referencia
```

Usan y recrean la base `tecba_test` (nunca la de desarrollo), con providers mock y sin LLM. CI corre lo mismo en cada push/PR.

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
