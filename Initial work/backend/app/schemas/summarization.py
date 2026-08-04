"""
Pydantic schemas for the Summarizer API.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Input payload for summarization."""
    text: str = Field(
        ...,
        min_length=50,
        max_length=50000,
        description="Sinhala article text to summarize",
    )
    length: Literal["short", "medium", "long"] = Field(
        "medium",
        description="Desired summary length: short (~2 sentences), medium (~1 paragraph), long (~3 paragraphs)",
    )


class SummarizeResponse(BaseModel):
    """Output payload after summarization."""
    id: str = Field(description="Unique summarization record ID")
    summary: str = Field(description="Generated summary in Sinhala")
    length: str = Field(description="Length preference used")
    created_at: datetime | None = Field(default=None)


class SummarizeHistoryResponse(BaseModel):
    """Paginated list of past summarizations."""
    items: list[SummarizeResponse]
    total: int
    page: int
    page_size: int
