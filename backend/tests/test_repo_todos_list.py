import uuid

from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.todos import create_todo, list_query, list_todos
from app.schemas.todo import TodoCreate


async def _user(session: AsyncSession) -> uuid.UUID:
    user = User(email=f"{uuid.uuid4()}@example.com", password_hash="x")
    session.add(user)
    await session.flush()
    return user.id


async def test_positions_increase_by_1024(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    positions = [
        (await create_todo(db_session, uid, TodoCreate(title=f"t{i}"))).position for i in range(3)
    ]
    assert positions == [1024.0, 2048.0, 3072.0]


async def test_pagination_walks_all(db_session: AsyncSession) -> None:
    uid = await _user(db_session)
    created = [(await create_todo(db_session, uid, TodoCreate(title=f"t{i}"))).id for i in range(5)]
    seen: list[uuid.UUID] = []
    sizes: list[int] = []
    after = None
    while True:
        rows, after = await list_todos(db_session, uid, 2, after)
        sizes.append(len(rows))
        seen.extend(r.id for r in rows)
        if after is None:
            break
    assert sizes == [2, 2, 1]
    assert seen == created
    assert len(set(seen)) == 5


async def test_other_users_todos_hidden(db_session: AsyncSession) -> None:
    a = await _user(db_session)
    b = await _user(db_session)
    await create_todo(db_session, a, TodoCreate(title="mine"))
    rows, nxt = await list_todos(db_session, b, 10, None)
    assert rows == []
    assert nxt is None


async def test_explain_uses_index(db_session: AsyncSession) -> None:
    stmt = list_query(uuid.uuid4(), 20, (1024.0, uuid.uuid4()))
    sql = str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    await db_session.execute(text("SET LOCAL enable_seqscan = off"))
    plan = "\n".join(r[0] for r in await db_session.execute(text("EXPLAIN " + sql)))
    assert "ix_todos_user_id_position_id" in plan
