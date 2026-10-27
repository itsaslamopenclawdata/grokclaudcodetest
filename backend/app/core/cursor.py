import base64
import binascii
import math
import uuid


class CursorError(ValueError):
    """Raised when a pagination cursor cannot be decoded."""


def encode_cursor(position: float, todo_id: uuid.UUID) -> str:
    raw = f"{position!r}:{todo_id}".encode()
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> tuple[float, uuid.UUID]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        pos_text, sep, id_text = raw.partition(":")
        if not sep:
            raise CursorError("missing separator")
        position = float(pos_text)
        if not math.isfinite(position):
            raise CursorError("non-finite position")
        return position, uuid.UUID(id_text)
    except CursorError:
        raise
    except (ValueError, binascii.Error, UnicodeError) as exc:
        raise CursorError(str(exc)) from exc
