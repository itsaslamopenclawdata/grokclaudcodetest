import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from app.core.config import Settings
from app.db.session import build_engine


async def test_select_one(db_session: AsyncSession) -> None:
    assert (await db_session.execute(text("select 1"))).scalar_one() == 1


def test_build_engine_nullpool() -> None:
    eng = build_engine(Settings(_env_file=None, db_use_nullpool=True))  # type: ignore[call-arg]
    assert isinstance(eng.pool, NullPool)


def test_build_engine_default_pool() -> None:
    eng = build_engine(Settings(_env_file=None, db_use_nullpool=False))  # type: ignore[call-arg]
    assert isinstance(eng.pool, AsyncAdaptedQueuePool)


async def test_sql_error_propagates(db_session: AsyncSession) -> None:
    with pytest.raises(DBAPIError):
        await db_session.execute(text("select 1/0"))
