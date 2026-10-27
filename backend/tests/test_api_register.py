import httpx

URL = "/api/v1/auth/register"


async def test_register_201(client: httpx.AsyncClient) -> None:
    r = await client.post(URL, json={"email": "alice@example.com", "password": "s3cret-pass"})
    assert r.status_code == 201
    body = r.json()
    assert {"id", "email", "created_at"} <= body.keys()
    assert "password" not in body
    assert "password_hash" not in body


async def test_register_lowercases_email(client: httpx.AsyncClient) -> None:
    r = await client.post(URL, json={"email": "Bob@Example.com", "password": "s3cret-pass"})
    assert r.status_code == 201
    assert r.json()["email"] == "bob@example.com"


async def test_register_duplicate_409(client: httpx.AsyncClient) -> None:
    payload = {"email": "carol@example.com", "password": "s3cret-pass"}
    assert (await client.post(URL, json=payload)).status_code == 201
    r = await client.post(URL, json=payload)
    assert r.status_code == 409
    assert r.json() == {"detail": "email already registered"}


async def test_register_short_password_422(client: httpx.AsyncClient) -> None:
    r = await client.post(URL, json={"email": "dave@example.com", "password": "short"})
    assert r.status_code == 422


async def test_register_bad_email_422(client: httpx.AsyncClient) -> None:
    r = await client.post(URL, json={"email": "not-an-email", "password": "s3cret-pass"})
    assert r.status_code == 422
