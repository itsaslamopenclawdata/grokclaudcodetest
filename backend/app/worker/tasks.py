import asyncio
import uuid
from datetime import UTC, datetime

import structlog
from celery import Task
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.worker.celery_app import celery_app

log = structlog.get_logger()

_MARK = text(
    "UPDATE todos SET reminded_at = now() WHERE id = :id AND reminded_at IS NULL RETURNING id"
)


async def mark_reminded(database_url: str, todo_id: uuid.UUID) -> bool:
    """Set reminded_at once. True only for the call that set it."""
    engine = create_async_engine(database_url, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            row = (await conn.execute(_MARK, {"id": todo_id})).first()
    finally:
        await engine.dispose()
    return row is not None


@celery_app.task(  # type: ignore[untyped-decorator]
    name="todos.send_reminder",
    bind=True,
    acks_late=True,
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    max_retries=5,
)
def send_reminder(self: Task, todo_id: str) -> bool:
    sent = asyncio.run(mark_reminded(get_settings().database_url, uuid.UUID(todo_id)))
    if sent:
        log.info("reminder.sent", todo_id=todo_id)
    return sent


_DUE = text(
    "SELECT id FROM todos WHERE reminded_at IS NULL AND remind_at IS NOT NULL"
    " AND remind_at <= :now ORDER BY remind_at LIMIT :limit"
)


async def due_ids(database_url: str, now: datetime, limit: int = 500) -> list[uuid.UUID]:
    """Due, unreminded todos (served by ix_todos_remind_pending)."""
    engine = create_async_engine(database_url, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            rows = (await conn.execute(_DUE, {"now": now, "limit": limit})).scalars().all()
    finally:
        await engine.dispose()
    return list(rows)


@celery_app.task(name="todos.scan_due_reminders")  # type: ignore[untyped-decorator]
def scan_due_reminders() -> int:
    ids = asyncio.run(due_ids(get_settings().database_url, datetime.now(UTC)))
    for todo_id in ids:
        send_reminder.delay(str(todo_id))
    log.info("reminder.scan", enqueued=len(ids))
    return len(ids)
