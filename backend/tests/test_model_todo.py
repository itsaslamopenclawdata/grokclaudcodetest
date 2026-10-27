import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Todo, User


async def _user(db_session: AsyncSession, email: str) -> User:
    user = User(email=email, password_hash="x")
    db_session.add(user)
    await db_session.flush()
    return user


async def test_insert_todo_defaults(db_session: AsyncSession) -> None:
    user = await _user(db_session, "t1@example.com")
    todo = Todo(user_id=user.id, title="buy milk", position=1.0)
    db_session.add(todo)
    await db_session.flush()
    await db_session.refresh(todo)
    assert todo.is_done is False
    assert todo.created_at is not None


async def test_empty_title_rejected(db_session: AsyncSession) -> None:
    user = await _user(db_session, "t2@example.com")
    db_session.add(Todo(user_id=user.id, title="", position=1.0))
    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_cascade_delete(db_session: AsyncSession) -> None:
    user = await _user(db_session, "t3@example.com")
    db_session.add(Todo(user_id=user.id, title="x", position=1.0))
    await db_session.flush()
    user_id = user.id
    await db_session.delete(user)
    await db_session.flush()
    db_session.expunge_all()
    rows = (await db_session.execute(select(Todo).where(Todo.user_id == user_id))).all()
    assert rows == []
