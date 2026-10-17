# Errores, límites y seguridad del API

Qué devuelve el API cuando algo sale mal y qué protecciones tiene. Código: `app/core/errors.py`, `app/core/rate_limit.py`, `app/schemas/limits.py`, `app/providers/http.py`.

## Formato único de error

Toda respuesta de error (4xx/5xx) tiene la misma forma:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Revisa los datos enviados.",
    "detail": [{ "field": "address", "message": "Campo obligatorio." }],
    "request_id": "a1b2c3d4e5f6"
  }
}
```

- `code`: estable, el frontend decide qué hacer según este valor.
- `message`: en español, listo para mostrar.
- `detail`: contexto extra. En validación es una lista `{field, message}`; puede ser `null`.
- `request_id`: el mismo valor que el header `X-Request-ID`.

| `code` | HTTP | Cuándo |
|---|---|---|
| `invalid_request` | 422 | Body o parámetros inválidos (campos faltantes, largo, coordenadas fuera de CABA, JSON inválido) |
| `not_found` | 404 | Ruta inexistente |
| `method_not_allowed` | 405 | Método no soportado en la ruta |
| `request_too_large` | 413 | `Content-Length` mayor a `MAX_REQUEST_BYTES` |
| `rate_limited` | 429 | Demasiadas consultas del mismo cliente. Incluye `Retry-After` |
| `database_unavailable` | 503 | `GET /ready` cuando la base no responde |
| `internal_error` | 500 | Cualquier error no previsto. Nunca incluye detalles internos |

Todos los errores están documentados en `/docs` (modelo `ErrorResponse`).

### Para quien escribe código

- Lanzar `AppError(ErrorCode.X, detail)` desde cualquier capa. No usar `HTTPException` ni `try/except` en las rutas: el middleware global ya convierte cualquier excepción en un 500 controlado (con traceback en el log).
- Caso nuevo: agregar el valor a `ErrorCode` y su `(status, mensaje)` a `ERROR_CATALOG`.

## Request id y logs

- Cada respuesta lleva `X-Request-ID`. Si el cliente manda uno, se respeta (máx. 64 caracteres imprimibles); si no, se genera.
- Cada línea de log incluye el request id: `fecha | nivel | request_id | logger | mensaje`, más una línea por request con método, ruta, status y duración. Con el id que ve el usuario se encuentra el error en los logs.

## Fuentes caídas: respuestas parciales, no 500

| Fuente | Si falla | Qué ve el frontend |
|---|---|---|
| USIG (geocoder) | `POST /locations/geocode` → `status: "unavailable"` | En `/consultations`: `status: "partial"`, `location.status: "unavailable"`, `data_status.warnings: ["geocoder_unavailable"]`. Requisitos, oficinas y fuentes se devuelven igual |
| epok | `zoning.status: "unavailable"` (ya existía) | `data_status.warnings: ["epok_unavailable"]`. El mensaje ya no incluye la excepción interna |
| LLM | Se usan las reglas locales (ya existía) | `/interpretations`: `fallback_reason` (`llm_unavailable`, `llm_rate_limited` o `llm_invalid_output`). `/consultations`: `data_status.warnings: ["llm_fallback_mock"]` |

Sin `LLM_API_KEY` no hay fallback que reportar: `fallback_reason` es `null` y no hay warning.

Las llamadas a USIG y epok usan un cliente HTTP compartido (`app/providers/http.py`) con `User-Agent`, reintentos de conexión (`HTTP_RETRIES`) y el timeout de cada proveedor.

## Límites de entrada

| Campo | Límite |
|---|---|
| `query` | 500 caracteres |
| `address`, `confirmed_location.normalized_address` | 200 caracteres |
| `activity_code`, `conversation_id` | 64 caracteres |
| `latitude` / `longitude` en `/locations/zoning` y `confirmed_location` | Dentro de CABA (lat −34,75…−34,50; lng −58,56…−58,30) |
| Body | `MAX_REQUEST_BYTES` (64 KiB por defecto) |

## Rate limit

- Aplica a `/consultations`, `/interpretations` y `/locations/*`, que son las rutas que llaman al LLM, USIG y epok. Catálogo, open-data, `/health` y `/ready` no tienen límite.
- Ventana deslizante de 1 minuto por IP, compartida entre esas rutas: `RATE_LIMIT_PER_MINUTE` (30 por defecto). Se desactiva con `RATE_LIMIT_ENABLED=false`.
- Es en memoria: cada proceso cuenta por separado. Alcanza para una sola instancia; con varias, pasarlo a Redis.
- Detrás del proxy del hosting, configurar `FORWARDED_ALLOW_IPS` (uvicorn corre con `--proxy-headers`) para que la IP sea la del cliente y no la del proxy.

## Health y readiness

| Ruta | Para qué |
|---|---|
| `GET /health` | Liveness: el proceso responde. No toca la base |
| `GET /ready` | Readiness: la base responde y el esquema está migrado. 503 `database_unavailable` si no |

## Configuración segura por defecto

| Variable | Default en código | Nota |
|---|---|---|
| `APP_ENV` | `production` | Solo con `local` se sincroniza el catálogo al arrancar. En producción el seed es un paso explícito (`RUN_SEED=true` o `python -m app.db.seed`) |
| `GEOCODER_PROVIDER` | `usig` | `mock` solo para desarrollo offline y tests |
| `DEBUG` | `false` | `true` loguea todas las queries SQL |
| `CORS_ORIGINS` | `localhost`/`127.0.0.1` en `:3000` y `:5173` | En producción, poner el dominio del frontend |
| `CORS_ALLOW_CREDENTIALS` | `false` | El MVP no usa cookies ni auth |

Si la API arranca con providers mock o `DEBUG=true` fuera de `local`/`test`, lo avisa en el log.

## Docker

- La imagen incluye Alembic. El entrypoint (`scripts/docker-entrypoint.sh`) corre `alembic upgrade head` (`RUN_MIGRATIONS`, default `true`) y opcionalmente el seed (`RUN_SEED`, default `false`) antes de levantar uvicorn.
- Corre sin root y tiene `HEALTHCHECK` sobre `/health`.

## Tests

- `scripts/test.sh` corre pytest dentro de la imagen de la API (Python 3.13) contra el Postgres del compose: `DB_PORT=5432 scripts/test.sh`. Usa y recrea la base `tecba_test`; nunca toca la de desarrollo.
- `tests/golden/`: respuestas exitosas de referencia de todos los endpoints con providers mock. Si un cambio las altera, el test falla. Para regenerarlas a propósito: `UPDATE_GOLDEN=1 scripts/test.sh -k golden` (y revisar el diff).
- CI (`.github/workflows/backend-ci.yml`): `ruff check` + `pytest` en cada push y PR, más el build de la imagen.

## Pendiente (fuera de este alcance)

- Sanitizar las URLs que vienen de snapshots externos (`map_layers`, `offices.url`) antes de mandarlas al frontend.
- Autenticación, si el producto la llega a necesitar.
