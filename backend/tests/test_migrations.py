import asyncio
import os
import subprocess
from collections.abc import Callable
from typing import Any

from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import create_async_engine

MIGRATE_DATABASE_URL = os.environ.get(
    "MIGRATE_DATABASE_URL", "postgresql+asyncpg://todo:todo@localhost:5432/todo_migrate"
)


def alembic(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "DATABASE_URL": MIGRATE_DATABASE_URL}
    return subprocess.run(
        ["uv", "run", "alembic", *args], env=env, capture_output=True, text=True, check=True
    )


def inspect_db(fn: Callable[[Any], Any]) -> Any:
    async def _run() -> Any:
        eng = create_async_engine(MIGRATE_DATABASE_URL)
        try:
            async with eng.connect() as conn:

                def _sync(sync_conn: Connection) -> Any:
                    return fn(inspect(sync_conn))

                return await conn.run_sync(_sync)
        finally:
            await eng.dispose()

    return asyncio.run(_run())


def test_upgrade_creates_users() -> None:
    alembic("downgrade", "base")
    alembic("upgrade", "0001")
    cols = inspect_db(lambda i: [c["name"] for c in i.get_columns("users")])
    assert cols == ["id", "email", "password_hash", "created_at"]


def test_downgrade_removes_users() -> None:
    alembic("upgrade", "0001")
    alembic("downgrade", "base")
    assert not inspect_db(lambda i: i.has_table("users"))


def test_cycle() -> None:
    alembic("upgrade", "head")
    alembic("downgrade", "-1")
    alembic("upgrade", "head")
