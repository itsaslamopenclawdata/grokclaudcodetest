import httpx

from tests.helpers import auth_headers

URL = "/api/v1/todos"


async def _create(client: httpx.AsyncClient, h: dict[str, str], title: str) -> str:
    r = await client.post(URL, json={"title": title}, headers=h)
    assert r.status_code == 201
    todo_id: str = r.json()["id"]
    return todo_id


async def test_patch_done_200(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    tid = await _create(client, h, "t")
    r = await client.patch(f"{URL}/{tid}", json={"is_done": True}, headers=h)
    assert r.status_code == 200
    assert r.json()["is_done"] is True


async def test_patch_position_changes_order(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    a, b, c = [await _create(client, h, n) for n in "abc"]
    r = await client.patch(f"{URL}/{c}", json={"position": 1536.0}, headers=h)
    assert r.status_code == 200
    items = (await client.get(URL, headers=h)).json()["items"]
    assert [i["id"] for i in items] == [a, c, b]


async def test_patch_empty_body_422(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    tid = await _create(client, h, "t")
    r = await client.patch(f"{URL}/{tid}", json={}, headers=h)
    assert r.status_code == 422


async def test_patch_other_users_todo_404(client: httpx.AsyncClient) -> None:
    ha = await auth_headers(client, "a@example.com")
    tid = await _create(client, ha, "t")
    hb = await auth_headers(client, "b@example.com")
    r = await client.patch(f"{URL}/{tid}", json={"title": "x"}, headers=hb)
    assert r.status_code == 404
    assert r.json() == {"detail": "todo not found"}


async def test_delete_204_then_404(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    tid = await _create(client, h, "t")
    assert (await client.delete(f"{URL}/{tid}", headers=h)).status_code == 204
    assert (await client.delete(f"{URL}/{tid}", headers=h)).status_code == 404


async def test_patch_bad_uuid_422(client: httpx.AsyncClient) -> None:
    h = await auth_headers(client, "a@example.com")
    r = await client.patch(f"{URL}/not-a-uuid", json={"title": "x"}, headers=h)
    assert r.status_code == 422
