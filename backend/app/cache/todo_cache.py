import uuid

from redis.asyncio import Redis

VERSION_TTL = 86400


def _ver_key(user_id: uuid.UUID) -> str:
    return f"app:todos_ver:{user_id}"


async def _page_key(r: Redis, user_id: uuid.UUID, cursor: str | None, limit: int) -> str:
    raw = await r.get(_ver_key(user_id))
    ver = "0" if raw is None else str(raw)
    return f"app:todos:{user_id}:v{ver}:{cursor or '-'}:{limit}"


async def get_page(r: Redis, user_id: uuid.UUID, cursor: str | None, limit: int) -> str | None:
    value = await r.get(await _page_key(r, user_id, cursor, limit))
    return None if value is None else str(value)


async def set_page(
    r: Redis, user_id: uuid.UUID, cursor: str | None, limit: int, payload_json: str, ttl: int
) -> None:
    await r.set(await _page_key(r, user_id, cursor, limit), payload_json, ex=ttl)


async def bump_version(r: Redis, user_id: uuid.UUID) -> None:
    key = _ver_key(user_id)
    async with r.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.expire(key, VERSION_TTL)
        await pipe.execute()
