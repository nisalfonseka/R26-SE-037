"""
SQLAlchemy ORM model for headline generation records.
"""

import uuid
from datetime import datetime

from sqlalchemy import Text, Integer, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HeadlineGeneration(Base):
    """Stores each headline generation request, candidates, and pipeline results."""

    __tablename__ = "headline_generations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Source input ──
    article_text: Mapped[str] = mapped_column(Text, nullable=False)

    # ── Generation config ──
    style: Mapped[str] = mapped_column(String(30), nullable=False, default="formal")

    max_length: Mapped[int] = mapped_column(Integer, default=80)

    # ── Output ──
    best_headline: Mapped[str] = mapped_column(Text, nullable=False)

    # List of candidate dicts: [{headline, rank, metrics, passed_validation}, ...]
    candidates: Mapped[list] = mapped_column(JSONB, default=list)

    # Entities extracted from the source article
    source_entities: Mapped[list] = mapped_column(JSONB, default=list)

    # Semantic extraction from best headline
    semantic_extraction: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Pipeline execution log
    pipeline_log: Mapped[list] = mapped_column(JSONB, default=list)

    # How many times regeneration was triggered
    regeneration_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<HeadlineGeneration id={self.id} "
            f"style={self.style} "
            f"regenerations={self.regeneration_count} "
            f"created_at={self.created_at}>"
        )
