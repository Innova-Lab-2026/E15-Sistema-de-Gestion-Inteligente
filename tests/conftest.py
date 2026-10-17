"""Shared test setup: isolated Postgres database, deterministic providers and a TestClient.

Environment variables are set before importing the app because settings and the DB engine
are created at import time. Tests never touch the development database: they recreate
TEST_DATABASE_URL (default `tecba_test`), run Alembic and the seed against it.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://tecba:tecba@localhost:5432/tecba_test",
)

os.environ.update(
    {
        "APP_ENV": "test",
        "DEBUG": "false",
        "DATABASE_URL": TEST_DATABASE_URL,
        # Deterministic providers: no network, no LLM.
        "GEOCODER_PROVIDER": "mock",
        "EPOK_PROVIDER": "mock",
        "LLM_BASE_URL": "",
        "LLM_API_KEY": "",
        # Enabled per test in test_rate_limit.py.
        "RATE_LIMIT_ENABLED": "false",
    }
)

import psycopg2  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _recreate_database(url: str) -> None:
    parsed = urlparse(url.replace("+asyncpg", ""))
    name = parsed.path.lstrip("/")
    if not name.endswith("_test"):
        raise RuntimeError(f"Refusing to recreate a non-test database: {name!r}")
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname="postgres",
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        cur.execute(f'CREATE DATABASE "{name}"')
    conn.close()


def _run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, env=os.environ.copy(), check=True)


@pytest.fixture(scope="session", autouse=True)
def database() -> None:
    _recreate_database(TEST_DATABASE_URL)
    _run("-m", "alembic", "upgrade", "head")
    _run("-m", "app.db.seed")


@pytest.fixture(scope="session")
def app(database):
    from app.main import app as fastapi_app

    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    # One TestClient (one event loop) for the whole session: the async engine pool is global.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def override_settings(app):
    """Run a test with modified Settings (e.g. a real provider pointing to a closed port)."""
    from app.core.config import get_settings

    def _override(**changes):
        patched = get_settings().model_copy(update=changes)
        app.dependency_overrides[get_settings] = lambda: patched
        return patched

    yield _override
    app.dependency_overrides.pop(get_settings, None)
