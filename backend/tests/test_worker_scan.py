import asyncio
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.config import get_settings
from app.models.todo import Todo
from app.models.user import User
from app.worker import tasks
from app.worker.celery_app import celery_app
from app.worker.tasks import due_ids
from tests.conftest import TEST_DATABASE_URL

NOW = datetime.now(UTC)
Make = Callable[..., Awaitable[uuid.UUID]]


@pytest.fixture
async def make_todo(test_engine: AsyncEngine) -> AsyncIterator[Make]:
    async with AsyncSession(test_engine, expire_on_commit=False) as s:
        user = User(email=f"scan-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
        s.add(user)
        await s.commit()
    pos = 0

    async def _make(remind_at: datetime | None, reminded_at: datetime | None = None) -> uuid.UUID:
        nonlocal pos
        pos += 1
        async with AsyncSession(test_engine, expire_on_commit=False) as s:
            t = Todo(
                user_id=user.id,
                title=f"t{pos}",
                position=pos,
                remind_at=remind_at,
                reminded_at=reminded_at,
            )
            s.add(t)
            await s.commit()
            return t.id

    yield _make
    async with AsyncSession(test_engine) as s:
        await s.execute(delete(Todo).where(Todo.user_id == user.id))
        await s.execute(delete(User).where(User.id == user.id))
        await s.commit()


async def test_due_ids_selects_only_due(make_todo: Make) -> None:
    due = await make_todo(NOW - timedelta(minutes=5))
    future = await make_todo(NOW + timedelta(hours=1))
    done = await make_todo(NOW - timedelta(minutes=5), reminded_at=NOW)
    none = await make_todo(None)
    ids = await due_ids(TEST_DATABASE_URL, NOW)
    assert due in ids
    assert future not in ids and done not in ids and none not in ids


async def test_due_ids_respects_limit(make_todo: Make) -> None:
    for m in (3, 2, 1):
        await make_todo(NOW - timedelta(minutes=m))
    assert len(await due_ids(TEST_DATABASE_URL, NOW, limit=2)) == 2


def test_beat_schedule_60s() -> None:
    entry = celery_app.conf.beat_schedule["scan-due-reminders"]
    assert entry["task"] == "todos.scan_due_reminders"
    assert entry["schedule"] == 60.0


async def test_scan_enqueues(make_todo: Make, monkeypatch: pytest.MonkeyPatch) -> None:
    a = await make_todo(NOW - timedelta(minutes=2))
    b = await make_todo(NOW - timedelta(minutes=1))
    await make_todo(NOW + timedelta(hours=1))
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    get_settings.cache_clear()
    delay = MagicMock()
    monkeypatch.setattr(tasks.send_reminder, "delay", delay)
    try:
        count = await asyncio.to_thread(tasks.scan_due_reminders)
    finally:
        get_settings.cache_clear()
    assert count == 2
    assert sorted(c.args[0] for c in delay.call_args_list) == sorted([str(a), str(b)])
