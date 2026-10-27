import httpx


async def test_health_ok(client: httpx.AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_health_post_not_allowed(client: httpx.AsyncClient) -> None:
    r = await client.post("/health")
    assert r.status_code == 405
