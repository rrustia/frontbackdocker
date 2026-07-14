from sqlalchemy import Column, Date, DateTime, Integer, String, Text, func

from .db import Base


class Task(Base):
    """I model the `tasks` table with explicit, readable fields.

    I stay intentionally small and explicit so teammates can understand the
    schema quickly without chasing mixins or extra abstraction layers.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="todo")
    priority = Column(String(16), nullable=False, default="medium")
    due_date = Column(Date, nullable=True)

    # I let the database generate timestamps so values stay consistent.
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
