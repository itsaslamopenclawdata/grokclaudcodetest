import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None)  # type: ignore[call-arg]


def test_hash_roundtrip() -> None:
    assert verify_password("s3cret-pass", hash_password("s3cret-pass")) is True


def test_wrong_password_false() -> None:
    h = hash_password("s3cret-pass")
    assert verify_password("nope", h) is False


def test_token_roundtrip(settings: Settings) -> None:
    uid = uuid.uuid4()
    assert decode_access_token(create_access_token(uid, settings), settings) == uid


def test_expired_token_rejected(settings: Settings) -> None:
    token = create_access_token(uuid.uuid4(), settings, now=datetime.now(UTC) - timedelta(hours=2))
    with pytest.raises(TokenError):
        decode_access_token(token, settings)


def test_tampered_token_rejected(settings: Settings) -> None:
    token = create_access_token(uuid.uuid4(), settings)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(TokenError):
        decode_access_token(tampered, settings)


def test_alg_none_rejected(settings: Settings) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "iat": now, "exp": now + timedelta(minutes=5)},
        key="",
        algorithm="none",
    )
    with pytest.raises(TokenError):
        decode_access_token(token, settings)
