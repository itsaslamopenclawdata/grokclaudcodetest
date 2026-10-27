import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class EmailTakenError(Exception):
    """Raised when a user with the same normalised email already exists."""


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == normalize_email(email)))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, email: str, password_hash: str) -> User:
    user = User(email=normalize_email(email), password_hash=password_hash)
    try:
        async with session.begin_nested():
            session.add(user)
            await session.flush()
    except IntegrityError as exc:
        raise EmailTakenError(user.email) from exc
    await session.commit()
    return user
