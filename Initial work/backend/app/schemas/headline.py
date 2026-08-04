"""
Pydantic schemas for the Headline Generation API.
Defines request/response shapes for the multi-stage headline pipeline.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ── Enums ──

class HeadlineStyle(str, Enum):
    """Supported headline style presets."""
    FORMAL = "formal"
    BREAKING_NEWS = "breaking_news"
    YOUTH = "youth"
    EDITORIAL = "editorial"


# ── Request ──

class HeadlineGenerateRequest(BaseModel):
    """Input payload for headline generation."""
    article_text: str = Field(
        ...,
        min_length=10,
        max_length=50000,
        description="Full Sinhala news article text to generate a headline for",
    )
    style: HeadlineStyle = Field(
        default=HeadlineStyle.FORMAL,
        description="Desired headline style/tone",
    )
    max_length: int = Field(
        default=80,
        ge=10,
        le=200,
        description="Maximum character length for the generated headline",
    )
    num_candidates: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of headline candidates to generate",
    )


# ── Nested detail models ──

class EntityInfo(BaseModel):
    """A named entity extracted from the article or headline."""
    text: str = Field(description="Entity surface form")
    label: str = Field(description="Entity type (PERSON, ORG, LOC, EVENT, etc.)")
    start: int = Field(description="Start character offset")
    end: int = Field(description="End character offset")


class ValidationMetrics(BaseModel):
    """Quality metrics computed during headline validation."""
    rouge_1: float = Field(default=0.0, ge=0.0, le=1.0, description="ROUGE-1 F1 score")
    rouge_2: float = Field(default=0.0, ge=0.0, le=1.0, description="ROUGE-2 F1 score")
    rouge_l: float = Field(default=0.0, ge=0.0, le=1.0, description="ROUGE-L F1 score")
    bleu: float = Field(default=0.0, ge=0.0, le=1.0, description="BLEU score")
    semantic_similarity: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Cosine similarity between article and headline embeddings",
    )
    entity_coverage: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Fraction of key entities preserved in headline",
    )
    grammar_pass: bool = Field(
        default=False,
        description="Whether the headline passed grammar validation",
    )
    length_ok: bool = Field(
        default=False,
        description="Whether the headline meets the length constraint",
    )


class SemanticExtraction(BaseModel):
    """Semantic themes and entities derived from the final headline."""
    key_themes: list[str] = Field(
        default_factory=list,
        description="Main themes/topics extracted from the headline",
    )
    entities: list[EntityInfo] = Field(
        default_factory=list,
        description="Named entities extracted from the headline",
    )
    visual_prompt: str = Field(
        default="",
        description="Auto-generated visual prompt for downstream image generation",
    )


class HeadlineCandidate(BaseModel):
    """A single generated headline candidate with its scores."""
    headline: str = Field(description="Generated headline text")
    rank: int = Field(description="Rank among candidates (1 = best)")
    metrics: ValidationMetrics = Field(description="Validation scores for this headline")
    passed_validation: bool = Field(
        default=False,
        description="Whether this candidate passed all quality thresholds",
    )


class PipelineStageLog(BaseModel):
    """Log entry for a single pipeline stage execution."""
    stage: str = Field(description="Pipeline stage name")
    status: str = Field(description="Stage status: success | warning | error")
    duration_ms: float = Field(description="Stage execution time in milliseconds")
    message: str = Field(default="", description="Optional stage message or detail")


# ── Response ──

class HeadlineGenerateResponse(BaseModel):
    """Output payload after headline generation pipeline completes."""
    id: str = Field(description="Unique generation record ID")
    best_headline: str = Field(description="Top-ranked headline")
    style: HeadlineStyle = Field(description="Style used for generation")
    candidates: list[HeadlineCandidate] = Field(
        default_factory=list,
        description="All generated headline candidates with metrics",
    )
    source_entities: list[EntityInfo] = Field(
        default_factory=list,
        description="Key entities extracted from the source article",
    )
    semantic_extraction: SemanticExtraction = Field(
        default_factory=SemanticExtraction,
        description="Semantic analysis of the best headline",
    )
    pipeline_log: list[PipelineStageLog] = Field(
        default_factory=list,
        description="Execution log for each pipeline stage",
    )
    regeneration_count: int = Field(
        default=0,
        description="Number of regeneration attempts before passing validation",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp of the generation",
    )


class HeadlineHistoryResponse(BaseModel):
    """Paginated list of past headline generations."""
    items: list[HeadlineGenerateResponse]
    total: int
    page: int
    page_size: int


# ── Image generation ──

class ImageGenerateRequest(BaseModel):
    """Request payload for visual prompt → image generation."""
    model_config = ConfigDict(protected_namespaces=())

    prompt: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="English visual prompt to send to the image generation model",
    )
    headline: str = Field(
        default="",
        description="Original Sinhala headline (used for alignment score calculation)",
    )
    model_id: str | None = Field(
        default=None,
        description="Optional image model id (overrides server IMAGEGEN_MODEL)",
    )
    key: str | None = Field(
        default=None,
        description="Optional API key for this single request",
    )


class ImageGenerateResponse(BaseModel):
    """Response after image generation."""
    image_url: str = Field(description="Generated image URL or data URI")
    alignment_score: str = Field(description="Semantic alignment: Low | Medium | High")
    prompt_used: str = Field(description="The exact prompt used for generation")
