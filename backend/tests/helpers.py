import httpx

PASSWORD = "s3cret-pass"


async def auth_headers(client: httpx.AsyncClient, email: str) -> dict[str, str]:
    creds = {"email": email, "password": PASSWORD}
    r = await client.post("/api/v1/auth/register", json=creds)
    assert r.status_code == 201, r.text
    r = await client.post("/api/v1/auth/login", json=creds)
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
