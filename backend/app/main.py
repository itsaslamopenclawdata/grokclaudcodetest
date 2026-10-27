from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, health, todos
from app.cache.redis import create_redis
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.metrics import setup_metrics
from app.core.request_id import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    s = get_settings()
    app.state.redis = create_redis(s.redis_url)
    app.state.redis_rl = create_redis(s.rate_limit_redis_url)
    yield
    await app.state.redis.aclose()
    await app.state.redis_rl.aclose()


def create_app() -> FastAPI:
    s = get_settings()
    configure_logging(s.log_level, s.log_json)
    app = FastAPI(
        title="Todo API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(todos.router)
    setup_metrics(app)
    return app


app = create_app()
