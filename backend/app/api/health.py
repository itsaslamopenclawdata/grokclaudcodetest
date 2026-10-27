from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import get_redis
from app.db.session import get_session

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"]


@router.get("/health", response_model=HealthOut, status_code=200)
async def health() -> HealthOut:
    return HealthOut(status="ok")


@router.get("/ready", responses={503: {"description": "a dependency is unreachable"}})
async def ready(
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> JSONResponse:
    db_status = redis_status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
    try:
        await redis.ping()
    except Exception:
        redis_status = "error"
    ok = db_status == redis_status == "ok"
    return JSONResponse(
        {"status": "ready" if ok else "not_ready", "db": db_status, "redis": redis_status},
        status_code=200 if ok else 503,
    )
