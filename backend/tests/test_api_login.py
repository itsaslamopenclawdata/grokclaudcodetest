import httpx

CREDS = {"email": "login@example.com", "password": "s3cret-pass"}


async def _register(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/v1/auth/register", json=CREDS)
    assert r.status_code == 201


async def test_login_200_returns_token_and_cookie(client: httpx.AsyncClient) -> None:
    await _register(client)
    r = await client.post("/api/v1/auth/login", json=CREDS)
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 3600
    assert body["access_token"]
    cookie = r.headers["set-cookie"]
    assert "access_token=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=strict" in cookie


async def test_login_wrong_password_401(client: httpx.AsyncClient) -> None:
    await _register(client)
    r = await client.post(
        "/api/v1/auth/login", json={"email": CREDS["email"], "password": "wrong-pass"}
    )
    assert r.status_code == 401
    assert r.json() == {"detail": "invalid credentials"}


async def test_login_unknown_email_401(client: httpx.AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "s3cret-pass"}
    )
    assert r.status_code == 401
    assert r.json() == {"detail": "invalid credentials"}


async def test_logout_clears_cookie(client: httpx.AsyncClient) -> None:
    r = await client.post("/api/v1/auth/logout")
    assert r.status_code == 204
    cookie = r.headers["set-cookie"]
    assert 'access_token=""' in cookie or "Max-Age=0" in cookie
