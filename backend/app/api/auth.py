from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import get_session
from app.models.user import User
from app.repositories.users import EmailTakenError, create_user
from app.schemas.auth import RegisterIn, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    responses={409: {"description": "email already registered"}},
)
async def register(
    body: RegisterIn, session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    try:
        return await create_user(session, body.email, hash_password(body.password))
    except EmailTakenError as exc:
        raise HTTPException(status_code=409, detail="email already registered") from exc
