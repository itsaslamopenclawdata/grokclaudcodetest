from collections.abc import AsyncIterator
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import Settings, get_settings


def build_engine(settings: Settings) -> AsyncEngine:
    if settings.db_use_nullpool:
        return create_async_engine(
            settings.database_url,
            poolclass=NullPool,
            connect_args={"prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__"},
        )
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )


engine: AsyncEngine = build_engine(get_settings())
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
