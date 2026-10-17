#!/usr/bin/env sh
# Corre pytest dentro de la imagen de la API (Python 3.13) contra el Postgres de docker compose.
# Uso: scripts/test.sh [args de pytest]   ·   DB_PORT=5434 scripts/test.sh -k golden
# Crea y recrea la base `tecba_test`; nunca toca la base de desarrollo.
# --entrypoint sh: el entrypoint de la imagen migra la base de desarrollo (DATABASE_URL del .env).
set -e
cd "$(dirname "$0")/.."
IMAGE="${TEST_IMAGE:-innova-oficial-api}"
DB_PORT="${DB_PORT:-5432}"
docker run --rm --network host --entrypoint sh \
  --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -e TEST_DATABASE_URL="postgresql+asyncpg://tecba:tecba@localhost:${DB_PORT}/tecba_test" \
  -e UPDATE_GOLDEN="${UPDATE_GOLDEN:-}" \
  -v "$PWD":/src -w /src "$IMAGE" \
  -c 'pip install -q --user --disable-pip-version-check -r requirements-dev.txt && python -m pytest -p no:cacheprovider "$@"' -- "$@"
