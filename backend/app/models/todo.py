import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Double,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Todo(Base):
    __tablename__ = "todos"
    __table_args__ = (
        CheckConstraint("char_length(title) BETWEEN 1 AND 200", name="title_len"),
        Index("ix_todos_user_id_position_id", "user_id", "position", "id"),
        Index(
            "ix_todos_remind_pending",
            "remind_at",
            postgresql_where=text("reminded_at IS NULL AND remind_at IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    is_done: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    position: Mapped[float] = mapped_column(Double)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remind_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
