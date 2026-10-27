import os

import httpx
from fastapi import FastAPI
from redis.asyncio import Redis

from app.cache.redis import create_redis, get_redis

TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")


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
