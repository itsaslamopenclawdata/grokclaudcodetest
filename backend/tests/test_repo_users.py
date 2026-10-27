import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users import (
    EmailTakenError,
    create_user,
    get_user_by_email,
    get_user_by_id,
)


async def test_create_and_get_by_email(db_session: AsyncSession) -> None:
    created = await create_user(db_session, " A@Example.com ", "hash")
    found = await get_user_by_email(db_session, "a@example.com")
    assert found is not None
    assert found.id == created.id
    assert found.email == "a@example.com"


async def test_get_by_id_unknown_returns_none(db_session: AsyncSession) -> None:
    assert await get_user_by_id(db_session, uuid.uuid4()) is None


async def test_duplicate_email_raises(db_session: AsyncSession) -> None:
    await create_user(db_session, "a@example.com", "hash")
    with pytest.raises(EmailTakenError):
        await create_user(db_session, "A@EXAMPLE.COM", "hash")
