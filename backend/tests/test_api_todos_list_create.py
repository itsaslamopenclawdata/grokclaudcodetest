import httpx

from tests.helpers import auth_headers

URL = "/api/v1/todos"


async def test_create_201(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    r = await client.post(URL, json={"title": "buy milk"}, headers=h)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "buy milk"
    assert body["is_done"] is False
    assert body["position"] == 1024.0


async def test_list_paginates(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    for i in range(3):
        assert (await client.post(URL, json={"title": f"t{i}"}, headers=h)).status_code == 201
    r = await client.get(URL, params={"limit": 2}, headers=h)
    assert r.status_code == 200
    page = r.json()
    assert len(page["items"]) == 2
    assert page["next_cursor"]
    r = await client.get(URL, params={"limit": 2, "cursor": page["next_cursor"]}, headers=h)
    page2 = r.json()
    assert len(page2["items"]) == 1
    assert page2["next_cursor"] is None


async def test_list_requires_auth_401(client: httpx.AsyncClient) -> None:
    r = await client.get(URL)
    assert r.status_code == 401


async def test_list_invalid_cursor_400(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    r = await client.get(URL, params={"cursor": "zzz"}, headers=h)
    assert r.status_code == 400
    assert r.json() == {"detail": "invalid cursor"}


async def test_limit_over_100_422(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    r = await client.get(URL, params={"limit": 101}, headers=h)
    assert r.status_code == 422


async def test_users_isolated(client: httpx.AsyncClient) -> None:
    ha = await auth_headers(client, "a@example.com")
    await client.post(URL, json={"title": "secret"}, headers=ha)
    hb = await auth_headers(client, "b@example.com")
    r = await client.get(URL, headers=hb)
    assert r.status_code == 200
    assert r.json()["items"] == []
