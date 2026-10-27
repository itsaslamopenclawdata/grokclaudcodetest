import os
from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI
from redis.asyncio import Redis

from app.cache.redis import create_redis, get_redis
from tests.helpers import auth_headers

TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")


@pytest.fixture(autouse=True)
async def _flush() -> AsyncIterator[None]:
    r = Redis.from_url(TEST_REDIS_URL)
    await r.flushdb()
    yield
    await r.aclose()


async def test_second_read_is_hit(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "c1@example.com")
    await client.post("/api/v1/todos", json={"title": "a"}, headers=h)
    r1 = await client.get("/api/v1/todos", headers=h)
    r2 = await client.get("/api/v1/todos", headers=h)
    assert r1.headers["X-Cache"] == "MISS"
    assert r2.headers["X-Cache"] == "HIT"
    assert r1.json() == r2.json()


async def test_create_invalidates(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "c2@example.com")
    await client.get("/api/v1/todos", headers=h)
    await client.post("/api/v1/todos", json={"title": "new"}, headers=h)
    r = await client.get("/api/v1/todos", headers=h)
    assert r.headers["X-Cache"] == "MISS"
    assert [t["title"] for t in r.json()["items"]] == ["new"]


async def test_patch_and_delete_invalidate(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "c3@example.com")
    tid = (await client.post("/api/v1/todos", json={"title": "x"}, headers=h)).json()["id"]
    await client.get("/api/v1/todos", headers=h)
    await client.patch(f"/api/v1/todos/{tid}", json={"title": "y"}, headers=h)
    r = await client.get("/api/v1/todos", headers=h)
    assert r.headers["X-Cache"] == "MISS"
    assert r.json()["items"][0]["title"] == "y"
    await client.delete(f"/api/v1/todos/{tid}", headers=h)
    r = await client.get("/api/v1/todos", headers=h)
    assert r.headers["X-Cache"] == "MISS"
    assert r.json()["items"] == []


async def test_redis_down_bypass(app: FastAPI, client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "c4@example.com")
    dead = create_redis("redis://localhost:1/0")
    app.dependency_overrides[get_redis] = lambda: dead
    r = await client.get("/api/v1/todos", headers=h)
    await dead.aclose()
    assert r.status_code == 200
    assert r.headers["X-Cache"] == "BYPASS"


async def test_cache_keys_per_user(client: httpx.AsyncClient) -> None:
    ha = await auth_headers(client, "c5a@example.com")
    hb = await auth_headers(client, "c5b@example.com")
    await client.get("/api/v1/todos", headers=ha)
    r = await client.get("/api/v1/todos", headers=hb)
    assert r.headers["X-Cache"] == "MISS"
