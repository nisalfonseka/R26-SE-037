"""
SQLAlchemy ORM model for summarization records.
"""

import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Summarization(Base):
    """Stores each news summarization request and its result."""

    __tablename__ = "summarizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Length preference: short | medium | long
    length_preference: Mapped[str] = mapped_column(String(20), default="medium")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Summarization id={self.id} length={self.length_preference}>"
