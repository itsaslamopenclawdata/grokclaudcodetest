from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.config import Settings, get_settings
from app.core.ratelimit import limit_login
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_session
from app.models.user import User
from app.repositories.users import EmailTakenError, create_user, get_user_by_email
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Verified against when the email is unknown so both failure paths cost one Argon2 check.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    responses={409: {"description": "email already registered"}},
)
async def register(body: RegisterIn, session: SessionDep) -> User:
    try:
        return await create_user(session, body.email, hash_password(body.password))
    except EmailTakenError as exc:
        raise HTTPException(status_code=409, detail="email already registered") from exc


@router.post(
    "/login",
    response_model=TokenOut,
    status_code=200,
    responses={
        401: {"description": "invalid credentials"},
        429: {"description": "rate limit exceeded"},
    },
    dependencies=[Depends(limit_login)],
)
async def login(
    body: LoginIn, response: Response, session: SessionDep, settings: SettingsDep
) -> TokenOut:
    user = await get_user_by_email(session, body.email)
    if user is None:
        verify_password(body.password, _DUMMY_HASH)
        raise HTTPException(status_code=401, detail="invalid credentials")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token(user.id, settings)
    max_age = settings.jwt_expires_minutes * 60
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="strict",
        secure=settings.env == "prod",
        max_age=max_age,
        path="/",
    )
    return TokenOut(access_token=token, expires_in=max_age)


@router.post("/logout", status_code=204)
async def logout(response: Response) -> None:
    response.delete_cookie("access_token", path="/")


@router.get("/me", response_model=UserOut, status_code=200)
async def me(user: CurrentUser) -> User:
    return user
