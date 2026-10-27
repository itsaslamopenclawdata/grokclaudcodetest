import asyncio
import uuid
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.config import get_settings
from app.models.todo import Todo
from app.models.user import User
from app.worker.celery_app import celery_app
from app.worker.tasks import mark_reminded, send_reminder
from tests.conftest import TEST_DATABASE_URL


@pytest.fixture
async def todo_id(test_engine: AsyncEngine) -> AsyncIterator[uuid.UUID]:
    """Committed rows (the task uses its own engine); removed afterwards."""
    async with AsyncSession(test_engine, expire_on_commit=False) as s:
        user = User(email=f"w-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        s.add(user)
        await s.flush()
        todo = Todo(user_id=user.id, title="remind me")
        s.add(todo)
        await s.commit()
    yield todo.id
    async with AsyncSession(test_engine) as s:
        await s.execute(delete(Todo).where(Todo.id == todo.id))
        await s.execute(delete(User).where(User.id == user.id))
        await s.commit()


async def _reminded_at(engine: AsyncEngine, tid: uuid.UUID) -> object:
    async with AsyncSession(engine) as s:
        return (await s.execute(select(Todo.reminded_at).where(Todo.id == tid))).scalar_one()


async def test_mark_reminded_once(todo_id: uuid.UUID, test_engine: AsyncEngine) -> None:
    assert await mark_reminded(TEST_DATABASE_URL, todo_id) is True
    assert await mark_reminded(TEST_DATABASE_URL, todo_id) is False
    assert await _reminded_at(test_engine, todo_id) is not None


async def test_unknown_id_false(test_engine: AsyncEngine) -> None:
    assert await mark_reminded(TEST_DATABASE_URL, uuid.uuid4()) is False


def test_task_registered() -> None:
    assert "todos.send_reminder" in celery_app.tasks


async def test_task_eager_runs(
    todo_id: uuid.UUID, test_engine: AsyncEngine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    get_settings.cache_clear()
    monkeypatch.setattr(celery_app.conf, "task_always_eager", True)
    try:
        # the task calls asyncio.run, so it needs a thread without a running loop
        result = await asyncio.to_thread(lambda: send_reminder.delay(str(todo_id)).get())
    finally:
        get_settings.cache_clear()
    assert result is True
    assert await _reminded_at(test_engine, todo_id) is not None
