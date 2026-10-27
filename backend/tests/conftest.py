import contextlib
import os
from collections.abc import AsyncIterator

import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://todo:todo@localhost:5432/todo_test"
)
TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")


@pytest.fixture(scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine(TEST_DATABASE_URL)
    with contextlib.suppress(ModuleNotFoundError):
        import app.models  # noqa: F401
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
async def app(db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[FastAPI]:
    """App with lifespan, test DB session and Redis DB 15 (flushed per test)."""
    monkeypatch.setenv("REDIS_URL", TEST_REDIS_URL)
    monkeypatch.setenv("RATE_LIMIT_REDIS_URL", TEST_REDIS_URL)
    get_settings.cache_clear()
    r = Redis.from_url(TEST_REDIS_URL)
    with contextlib.suppress(Exception):
        await r.flushdb()
    await r.aclose()
    application = create_app()

    async def _override() -> AsyncIterator[AsyncSession]:
        yield db_session

    application.dependency_overrides[get_session] = _override
    async with LifespanManager(application):
        yield application
    get_settings.cache_clear()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
