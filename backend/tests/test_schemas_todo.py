from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.todo import TodoCreate, TodoUpdate


def test_title_stripped() -> None:
    assert TodoCreate(title="  hi ").title == "hi"


def test_blank_title_rejected() -> None:
    with pytest.raises(ValidationError):
        TodoCreate(title="   ")


def test_title_201_chars_rejected() -> None:
    with pytest.raises(ValidationError):
        TodoCreate(title="x" * 201)


def test_naive_datetime_rejected() -> None:
    with pytest.raises(ValidationError):
        TodoCreate(title="hi", due_at=datetime(2030, 1, 1))


def test_empty_update_rejected() -> None:
    with pytest.raises(ValidationError):
        TodoUpdate()


def test_update_nan_position_rejected() -> None:
    with pytest.raises(ValidationError):
        TodoUpdate(position=float("nan"))
