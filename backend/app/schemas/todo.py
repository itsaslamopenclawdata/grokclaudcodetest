import uuid
from datetime import datetime
from typing import Annotated, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class TodoCreate(BaseModel):
    title: Title
    notes: str | None = Field(default=None, max_length=2000)
    due_at: AwareDatetime | None = None
    remind_at: AwareDatetime | None = None


class TodoUpdate(BaseModel):
    title: Title | None = None
    notes: str | None = Field(default=None, max_length=2000)
    is_done: bool | None = None
    position: float | None = Field(default=None, allow_inf_nan=False)
    due_at: AwareDatetime | None = None
    remind_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def _non_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("no fields to update")
        return self


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    notes: str | None
    is_done: bool
    position: float
    due_at: datetime | None
    remind_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TodoPage(BaseModel):
    items: list[TodoOut]
    next_cursor: str | None
