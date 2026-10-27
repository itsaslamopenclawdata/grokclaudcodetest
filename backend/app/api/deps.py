from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import TokenError, decode_access_token
from app.db.session import get_session
from app.models.user import User
from app.repositories.users import get_user_by_id


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401, detail="not authenticated", headers={"WWW-Authenticate": "Bearer"}
    )


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    auth = request.headers.get("Authorization", "")
    token = auth[len("Bearer ") :] if auth.startswith("Bearer ") else None
    if token is None:
        token = request.cookies.get("access_token")
    if not token:
        raise _unauthorized()
    try:
        user_id = decode_access_token(token, settings)
    except TokenError as exc:
        raise _unauthorized() from exc
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise _unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
