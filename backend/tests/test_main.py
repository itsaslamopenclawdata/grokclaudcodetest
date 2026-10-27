import httpx

from app.main import create_app


def test_create_app_title() -> None:
    assert create_app().title == "Todo API"


async def test_openapi_served(client: httpx.AsyncClient) -> None:
    r = await client.get("/api/openapi.json")
    assert r.status_code == 200
    assert r.json()["info"]["title"] == "Todo API"


async def test_unknown_route_404(client: httpx.AsyncClient) -> None:
    r = await client.get("/nope")
    assert r.status_code == 404
