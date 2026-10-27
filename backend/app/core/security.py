import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings


class TokenError(Exception):
    """Raised when an access token is invalid, expired or malformed."""


_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password, password_hash)
    except Exception:
        return False


def create_access_token(subject: uuid.UUID, settings: Settings, now: datetime | None = None) -> str:
    issued = now or datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "iat": issued,
        "exp": issued + timedelta(minutes=settings.jwt_expires_minutes),
    }
    return jwt.encode(
        payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str, settings: Settings) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise TokenError(str(exc)) from exc
