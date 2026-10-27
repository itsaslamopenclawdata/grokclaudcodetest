import asyncio
import uuid

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
