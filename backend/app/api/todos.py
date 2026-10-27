import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.cursor import CursorError, decode_cursor, encode_cursor
from app.db.session import get_session
from app.models.todo import Todo
from app.repositories.todos import create_todo, delete_todo, list_todos, update_todo
from app.schemas.todo import TodoCreate, TodoOut, TodoPage, TodoUpdate

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=TodoPage, responses={400: {"description": "invalid cursor"}})
async def list_(
    user: CurrentUser,
    session: SessionDep,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> TodoPage:
    after = None
    if cursor is not None:
        try:
            after = decode_cursor(cursor)
        except CursorError as exc:
            raise HTTPException(status_code=400, detail="invalid cursor") from exc
    rows, nxt = await list_todos(session, user.id, limit, after)
    return TodoPage(
        items=[TodoOut.model_validate(r) for r in rows],
        next_cursor=encode_cursor(*nxt) if nxt else None,
    )


@router.post("", response_model=TodoOut, status_code=201)
async def create(body: TodoCreate, user: CurrentUser, session: SessionDep) -> Todo:
    return await create_todo(session, user.id, body)


NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"description": "todo not found"}}


@router.patch("/{todo_id}", response_model=TodoOut, responses=NOT_FOUND)
async def update(
    todo_id: uuid.UUID, body: TodoUpdate, user: CurrentUser, session: SessionDep
) -> Todo:
    todo = await update_todo(session, user.id, todo_id, body)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo


@router.delete("/{todo_id}", status_code=204, responses=NOT_FOUND)
async def delete(todo_id: uuid.UUID, user: CurrentUser, session: SessionDep) -> None:
    if not await delete_todo(session, user.id, todo_id):
        raise HTTPException(status_code=404, detail="todo not found")
