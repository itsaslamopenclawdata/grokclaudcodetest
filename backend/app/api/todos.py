from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.cursor import CursorError, decode_cursor, encode_cursor
from app.db.session import get_session
from app.models.todo import Todo
from app.repositories.todos import create_todo, list_todos
from app.schemas.todo import TodoCreate, TodoOut, TodoPage

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
