import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def test_insert_and_read_user(db_session: AsyncSession) -> None:
    user = User(email="a@example.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()
    user_id = user.id
    db_session.expire_all()
    got = await db_session.get(User, user_id)
    assert got is not None
    assert got.email == "a@example.com"
    assert got.created_at is not None


async def test_duplicate_email_rejected(db_session: AsyncSession) -> None:
    db_session.add(User(email="dup@example.com", password_hash="x"))
    db_session.add(User(email="dup@example.com", password_hash="y"))
    with pytest.raises(IntegrityError):
        await db_session.flush()
