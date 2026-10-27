import httpx


async def test_metrics_endpoint_exposes_counter(client: httpx.AsyncClient) -> None:
    await client.get("/nope")
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


async def test_metrics_excludes_health(client: httpx.AsyncClient) -> None:
    await client.get("/health")
    r = await client.get("/metrics")
    assert 'handler="/health"' not in r.text
