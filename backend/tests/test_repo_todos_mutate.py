import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.models.user import User
from app.repositories.todos import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)
from app.schemas.todo import TodoCreate, TodoUpdate


async def _user(session: AsyncSession) -> uuid.UUID:
    user = User(email=f"{uuid.uuid4()}@example.com", password_hash="x")
    session.add(user)
    await session.flush()
    return user.id


async def _todo(session: AsyncSession, uid: uuid.UUID, title: str = "t") -> Todo:
    return await create_todo(session, uid, TodoCreate(title=title))


async def test_update_title_and_done(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    todo = await _todo(db_session, uid)
    before = todo.updated_at
    updated = await update_todo(db_session, uid, todo.id, TodoUpdate(title="new", is_done=True))
    assert updated is not None
    fetched = await get_todo(db_session, uid, todo.id)
    assert fetched is not None
    assert (fetched.title, fetched.is_done) == ("new", True)
    assert fetched.updated_at >= before


async def test_update_position_reorders(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    a, b, c = [await _todo(db_session, uid, n) for n in "abc"]
    await update_todo(db_session, uid, c.id, TodoUpdate(position=1536.0))
    rows, _ = await list_todos(db_session, uid, 10, None)
    assert [r.id for r in rows] == [a.id, c.id, b.id]


async def test_update_remind_at_resets_reminded_at(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    todo = await _todo(db_session, uid)
    todo.reminded_at = datetime.now(UTC)
    await db_session.commit()
    new_remind = datetime.now(UTC) + timedelta(days=1)
    updated = await update_todo(db_session, uid, todo.id, TodoUpdate(remind_at=new_remind))
    assert updated is not None
    assert updated.remind_at == new_remind
    assert updated.reminded_at is None


async def test_update_other_users_todo_returns_none(db_session: AsyncSession) -> None:
    owner = await _user(db_session)
    other = await _user(db_session)
    todo = await _todo(db_session, owner, "orig")
    assert await update_todo(db_session, other, todo.id, TodoUpdate(title="hacked")) is None
    fetched = await get_todo(db_session, owner, todo.id)
    assert fetched is not None
    assert fetched.title == "orig"


async def test_delete_other_users_todo_returns_false(db_session: AsyncSession) -> None:
    owner = await _user(db_session)
    other = await _user(db_session)
    todo = await _todo(db_session, owner)
    assert await delete_todo(db_session, other, todo.id) is False
    assert await get_todo(db_session, owner, todo.id) is not None


async def test_delete_own_returns_true_then_get_none(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    todo = await _todo(db_session, uid)
    assert await delete_todo(db_session, uid, todo.id) is True
    assert await get_todo(db_session, uid, todo.id) is None
