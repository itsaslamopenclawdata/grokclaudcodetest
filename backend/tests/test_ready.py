import os
from collections.abc import AsyncIterator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import create_redis, get_redis
from app.core.config import get_settings
from app.db.session import get_session
from app.main import create_app

TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")


@pytest.fixture
async def app(db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[FastAPI]:
    monkeypatch.setenv("REDIS_URL", TEST_REDIS_URL)
    monkeypatch.setenv("RATE_LIMIT_REDIS_URL", TEST_REDIS_URL)
    get_settings.cache_clear()
    application = create_app()

    async def _session() -> AsyncIterator[AsyncSession]:
        yield db_session

    application.dependency_overrides[get_session] = _session
    async with LifespanManager(application):
        yield application
    get_settings.cache_clear()


async def _get(app: FastAPI, path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        return await c.get(path)


def _dead_redis(app: FastAPI) -> Redis:
    dead = create_redis("redis://localhost:1/0")
    app.dependency_overrides[get_redis] = lambda: dead
    return dead


async def test_ready_200(app: FastAPI) -> None:
    r = await _get(app, "/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready", "db": "ok", "redis": "ok"}


async def test_ready_503_when_redis_down(app: FastAPI) -> None:
    dead = _dead_redis(app)
    r = await _get(app, "/ready")
    await dead.aclose()
    assert r.status_code == 503
    assert r.json()["redis"] == "error"
    assert r.json()["db"] == "ok"


async def test_health_still_200_when_redis_down(app: FastAPI) -> None:
    dead = _dead_redis(app)
    r = await _get(app, "/health")
    await dead.aclose()
    assert r.status_code == 200
