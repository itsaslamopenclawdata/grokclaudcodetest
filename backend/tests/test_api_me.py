import uuid

import httpx

from app.core.config import Settings
from app.core.security import create_access_token

CREDS = {"email": "me@example.com", "password": "s3cret-pass"}


async def _login(client: httpx.AsyncClient) -> str:
    assert (await client.post("/api/v1/auth/register", json=CREDS)).status_code == 201
    r = await client.post("/api/v1/auth/login", json=CREDS)
    assert r.status_code == 200
    token: str = r.json()["access_token"]
    return token


async def test_me_with_bearer(client: httpx.AsyncClient) -> None:
    token = await _login(client)
    client.cookies.clear()
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == CREDS["email"]


async def test_me_with_cookie(client: httpx.AsyncClient) -> None:
    await _login(client)
    assert client.cookies.get("access_token")
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == CREDS["email"]


async def test_me_missing_token_401(client: httpx.AsyncClient) -> None:
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


async def test_me_garbage_token_401(client: httpx.AsyncClient) -> None:
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer abc"})
    assert r.status_code == 401


async def test_me_token_for_missing_user_401(client: httpx.AsyncClient) -> None:
    token = create_access_token(uuid.uuid4(), Settings(_env_file=None))  # type: ignore[call-arg]
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
