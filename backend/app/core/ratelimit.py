import time
from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.api.deps import CurrentUser
from app.cache.redis import get_rl_redis
from app.core.config import Settings, get_settings

log = structlog.get_logger()

RLRedis = Annotated[Redis, Depends(get_rl_redis)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def hit(
    r: Redis, prefix: str, subject: str, limit: int, now: float | None = None
) -> int | None:
    """Fixed one-minute window. None if allowed, else seconds until the window resets."""
    ts = time.time() if now is None else now
    minute = int(ts // 60)
    key = f"app:ratelimit:{prefix}:{subject}:{minute}"
    count = int(await r.incr(key))
    if count == 1:
        await r.expire(key, 60)
    if count <= limit:
        return None
    return max(1, int((minute + 1) * 60 - ts))


async def _enforce(r: Redis, prefix: str, subject: str, limit: int) -> None:
    try:
        secs = await hit(r, prefix, subject, limit)
    except RedisError as exc:
        log.warning("ratelimit.redis_error", prefix=prefix, error=str(exc))
        return
    if secs is not None:
        raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": str(secs)})


def client_ip(request: Request, s: Settings) -> str:
    if s.trust_proxy_headers and (real := request.headers.get("x-real-ip")):
        return real
    return request.client.host if request.client else "unknown"


async def limit_todos(user: CurrentUser, r: RLRedis, s: SettingsDep) -> None:
    await _enforce(r, "todos", str(user.id), s.rate_limit_per_minute)


async def limit_login(request: Request, r: RLRedis, s: SettingsDep) -> None:
    await _enforce(r, "login", client_ip(request, s), s.login_rate_limit_per_minute)
