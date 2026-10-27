import re

import httpx
import structlog

HEX32 = re.compile(r"^[0-9a-f]{32}$")


async def test_generates_request_id(client: httpx.AsyncClient) -> None:
    r = await client.get("/nope")
    assert HEX32.match(r.headers["X-Request-ID"])


async def test_keeps_valid_incoming_id(client: httpx.AsyncClient) -> None:
    r = await client.get("/nope", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"


async def test_replaces_invalid_incoming_id(client: httpx.AsyncClient) -> None:
    bad = "a" * 200
    r = await client.get("/nope", headers={"X-Request-ID": bad})
    rid = r.headers["X-Request-ID"]
    assert rid != bad
    assert HEX32.match(rid)


async def test_logs_request_completed(client: httpx.AsyncClient) -> None:
    with structlog.testing.capture_logs() as logs:
        await client.get("/nope")
    done = [e for e in logs if e.get("event") == "request.completed"]
    assert len(done) == 1
    assert done[0]["status_code"] == 404
    assert done[0]["path"] == "/nope"
