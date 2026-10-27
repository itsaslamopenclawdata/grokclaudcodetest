import uuid
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.cache.redis import get_redis
from app.cache.todo_cache import bump_version, get_page, set_page
from app.core.config import Settings, get_settings
from app.core.cursor import CursorError, decode_cursor, encode_cursor
from app.db.session import get_session
from app.models.todo import Todo
from app.repositories.todos import create_todo, delete_todo, list_todos, update_todo
from app.schemas.todo import TodoCreate, TodoOut, TodoPage, TodoUpdate

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
log = structlog.get_logger()


async def _invalidate(r: Redis, user_id: uuid.UUID) -> None:
    try:
        await bump_version(r, user_id)
    except RedisError as exc:
        log.warning("cache.invalidate_failed", user_id=str(user_id), error=str(exc))


@router.get("", response_model=TodoPage, responses={400: {"description": "invalid cursor"}})
async def list_(
    user: CurrentUser,
    session: SessionDep,
    r: RedisDep,
    settings: SettingsDep,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> Response:
    after = None
    if cursor is not None:
        try:
            after = decode_cursor(cursor)
        except CursorError as exc:
            raise HTTPException(status_code=400, detail="invalid cursor") from exc
    status = "MISS"
    try:
        cached = await get_page(r, user.id, cursor, limit)
    except RedisError:
        cached, status = None, "BYPASS"
    if cached is not None:
        return Response(cached, media_type="application/json", headers={"X-Cache": "HIT"})
    rows, nxt = await list_todos(session, user.id, limit, after)
    payload = TodoPage(
        items=[TodoOut.model_validate(x) for x in rows],
        next_cursor=encode_cursor(*nxt) if nxt else None,
    ).model_dump_json()
    if status == "MISS":
        try:
            await set_page(r, user.id, cursor, limit, payload, settings.list_cache_ttl_seconds)
        except RedisError:
            status = "BYPASS"
    return Response(payload, media_type="application/json", headers={"X-Cache": status})


@router.post("", response_model=TodoOut, status_code=201)
async def create(body: TodoCreate, user: CurrentUser, session: SessionDep, r: RedisDep) -> Todo:
    todo = await create_todo(session, user.id, body)
    await _invalidate(r, user.id)
    return todo


NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"description": "todo not found"}}


@router.patch("/{todo_id}", response_model=TodoOut, responses=NOT_FOUND)
async def update(
    todo_id: uuid.UUID, body: TodoUpdate, user: CurrentUser, session: SessionDep, r: RedisDep
) -> Todo:
    todo = await update_todo(session, user.id, todo_id, body)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    await _invalidate(r, user.id)
    return todo


@router.delete("/{todo_id}", status_code=204, responses=NOT_FOUND)
async def delete(todo_id: uuid.UUID, user: CurrentUser, session: SessionDep, r: RedisDep) -> None:
    if not await delete_todo(session, user.id, todo_id):
        raise HTTPException(status_code=404, detail="todo not found")
    await _invalidate(r, user.id)
