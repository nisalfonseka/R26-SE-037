"""
Pydantic schemas for the Style Rewriter API.
Defines request/response shapes independently of ORM models.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ── Request ──

class StyleRewriteRequest(BaseModel):
    """Input payload for style rewriting."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Sinhala text to rewrite",
    )
    tone: str = Field(
        ...,
        description="Target writing style (formal, editorial, sports, youth, children, breaking)",
    )


# ── Response ──

class StyleRewriteResponse(BaseModel):
    """Output payload after style rewriting."""
    id: str = Field(description="Unique rewrite record ID")
    original: str = Field(description="Original input text")
    rewritten: str = Field(description="Rewritten text in target style")
    tone: str = Field(description="Applied writing style")
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp of the rewrite",
    )


class StyleHistoryResponse(BaseModel):
    """Paginated list of past style rewrites."""
    items: list[StyleRewriteResponse]
    total: int
    page: int
    page_size: int