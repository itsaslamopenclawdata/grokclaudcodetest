import base64
import uuid

import pytest

from app.core.cursor import CursorError, decode_cursor, encode_cursor


def test_roundtrip() -> None:
    u = uuid.uuid4()
    assert decode_cursor(encode_cursor(1536.25, u)) == (1536.25, u)


def test_no_padding() -> None:
    for pos in (1.0, 1536.25, 0.1, 12345.678):
        assert "=" not in encode_cursor(pos, uuid.uuid4())


def test_garbage_raises() -> None:
    valid_b64_of_x_y = base64.urlsafe_b64encode(b"x:y").decode().rstrip("=")
    for bad in ("!!!", "bm9jb2xvbg", valid_b64_of_x_y):
        with pytest.raises(CursorError):
            decode_cursor(bad)
