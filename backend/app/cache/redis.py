from fastapi import Request
from redis.asyncio import Redis


def create_redis(url: str) -> Redis:
    return Redis.from_url(url, decode_responses=True, socket_timeout=0.5)


def get_redis(request: Request) -> Redis:
    """Cache client (DB 0)."""
    client: Redis = request.app.state.redis
    return client


def get_rl_redis(request: Request) -> Redis:
    """Rate-limit client (DB 1)."""
    client: Redis = request.app.state.redis_rl
    return client
