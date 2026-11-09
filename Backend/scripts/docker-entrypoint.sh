#!/bin/sh
# Container entrypoint: apply migrations (and optionally the catalog seed), then start the API.
#   RUN_MIGRATIONS=false  skip `alembic upgrade head` (default: true)
#   RUN_SEED=true         run `python -m app.db.seed` after migrating (default: false; with
#                         APP_ENV=local the API also syncs the catalog on startup)
#   FORWARDED_ALLOW_IPS   read by uvicorn: proxies trusted for X-Forwarded-For (default 127.0.0.1).
#                         Behind a hosting proxy set it so rate limiting sees the real client IP.
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

if [ "${RUN_SEED:-false}" = "true" ]; then
  python -m app.db.seed
fi

exec "$@"
