"""
SQLAlchemy ORM model for style rewrite history.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class StyleRewrite(Base):
    """Stores style rewriting history."""

    __tablename__ = "style_rewrites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_text = Column(Text, nullable=False)
    rewritten_text = Column(Text, nullable=False)
    target_style = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)