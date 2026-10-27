import uuid

from sqlalchemy import Select, delete, func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

POSITION_STEP = 1024.0

Keyset = tuple[float, uuid.UUID]


async def create_todo(session: AsyncSession, user_id: uuid.UUID, data: TodoCreate) -> Todo:
    max_pos = await session.scalar(
        select(func.coalesce(func.max(Todo.position), 0.0)).where(Todo.user_id == user_id)
    )
    todo = Todo(
        user_id=user_id,
        title=data.title,
        notes=data.notes,
        due_at=data.due_at,
        remind_at=data.remind_at,
        position=float(max_pos or 0.0) + POSITION_STEP,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


def list_query(user_id: uuid.UUID, limit: int, after: Keyset | None) -> Select[Todo]:
    stmt = select(Todo).where(Todo.user_id == user_id)
    if after is not None:
        stmt = stmt.where(tuple_(Todo.position, Todo.id) > tuple_(after[0], after[1]))
    return stmt.order_by(Todo.position, Todo.id).limit(limit + 1)


async def list_todos(
    session: AsyncSession, user_id: uuid.UUID, limit: int, after: Keyset | None
) -> tuple[list[Todo], Keyset | None]:
    rows = list((await session.scalars(list_query(user_id, limit, after))).all())
    if len(rows) > limit:
        rows = rows[:limit]
        return rows, (rows[-1].position, rows[-1].id)
    return rows, None


async def get_todo(session: AsyncSession, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo | None:
    result = await session.scalars(select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id))
    return result.one_or_none()


async def update_todo(
    session: AsyncSession, user_id: uuid.UUID, todo_id: uuid.UUID, data: TodoUpdate
) -> Todo | None:
    todo = await get_todo(session, user_id, todo_id)
    if todo is None:
        return None
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(todo, field, value)
    if "remind_at" in changes:
        todo.reminded_at = None
    await session.commit()
    await session.refresh(todo)
    return todo


async def delete_todo(session: AsyncSession, user_id: uuid.UUID, todo_id: uuid.UUID) -> bool:
    result = await session.execute(
        delete(Todo).where(Todo.id == todo_id, Todo.user_id == user_id).returning(Todo.id)
    )
    deleted = result.scalar_one_or_none() is not None
    await session.commit()
    return deleted
