import httpx
import pytest
from fastapi import FastAPI

from app.cache.redis import create_redis, get_rl_redis
from app.core.config import Settings, get_settings
from app.core.ratelimit import hit
from tests.helpers import PASSWORD, auth_headers


@pytest.fixture
def limited(app: FastAPI) -> FastAPI:
    s = get_settings().model_copy(
        update={"rate_limit_per_minute": 3, "login_rate_limit_per_minute": 2}
    )
    app.dependency_overrides[get_settings] = lambda: s
    return app


async def test_hit_allows_then_blocks(app: FastAPI) -> None:
    r = app.state.redis_rl
    now = 1_700_000_010.0
    assert await hit(r, "t", "s1", 2, now=now) is None
    assert await hit(r, "t", "s1", 2, now=now) is None
    secs = await hit(r, "t", "s1", 2, now=now)
    assert secs is not None and 1 <= secs <= 60
    assert await hit(r, "t", "s1", 2, now=now + 60) is None


async def test_todos_429_after_limit(limited: FastAPI, client: httpx.AsyncClient) -> None:
    s: Settings = limited.dependency_overrides[get_settings]()
    s2 = s.model_copy(update={"login_rate_limit_per_minute": 100})
    limited.dependency_overrides[get_settings] = lambda: s2
    h = await auth_headers(client, "rl1@example.com")
    for _ in range(3):
        assert (await client.get("/api/v1/todos", headers=h)).status_code == 200
    r = await client.get("/api/v1/todos", headers=h)
    assert r.status_code == 429
    assert 1 <= int(r.headers["Retry-After"]) <= 60


async def test_login_429_per_ip(limited: FastAPI, client: httpx.AsyncClient) -> None:
    creds = {"email": "rl2@example.com", "password": PASSWORD}
    codes = [(await client.post("/api/v1/auth/login", json=creds)).status_code for _ in range(3)]
    assert codes[:2] != [429, 429]
    assert codes[2] == 429


async def test_x_real_ip_ignored_when_untrusted(
    limited: FastAPI, client: httpx.AsyncClient
) -> None:
    creds = {"email": "rl3@example.com", "password": PASSWORD}
    for i in range(2):
        await client.post("/api/v1/auth/login", json=creds, headers={"X-Real-IP": f"10.0.0.{i}"})
    r = await client.post("/api/v1/auth/login", json=creds, headers={"X-Real-IP": "10.0.0.9"})
    assert r.status_code == 429


async def test_fail_open_when_redis_down(limited: FastAPI, client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "rl4@example.com")
    dead = create_redis("redis://localhost:1/0")
    limited.dependency_overrides[get_rl_redis] = lambda: dead
    r = await client.get("/api/v1/todos", headers=h)
    await dead.aclose()
    assert r.status_code == 200
