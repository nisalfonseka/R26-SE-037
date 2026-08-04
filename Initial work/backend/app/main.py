"""
FastAPI application entrypoint.

- CORS middleware
- Lifespan handler (DB init/cleanup)
- Router registration
- Global health check
"""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db, close_db

# Import all ORM models so SQLAlchemy metadata is populated before init_db()
import app.models  # noqa: F401  (side-effect import)

from app.api.v1 import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: dispose engine."""
    await init_db()
    yield
    await close_db()


settings = get_settings()

app = FastAPI(
    title="SinAI — Sinhala Journalism LLM API",
    description="Backend API for Sinhala grammar checking, headline generation, style rewriting, and summarization.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
# In development use wildcard so any localhost port works (Vite, Storybook, etc.)
# In production, lock down to the explicit origin list in .env
_cors_origins = ["*"] if settings.is_development else settings.cors_origin_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,   # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handlers ──

@app.exception_handler(httpx.HTTPStatusError)
async def openrouter_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """Convert upstream OpenRouter HTTP errors into clean API responses."""
    status = exc.response.status_code
    if status == 429:
        return JSONResponse(
            status_code=503,
            content={
                "detail": (
                    "The AI service is temporarily rate-limited. "
                    "Please wait a few seconds and try again."
                )
            },
        )
    return JSONResponse(
        status_code=502,
        content={"detail": f"Upstream AI API error ({status}). Please try again."},
    )


# ── Routers ──
app.include_router(v1_router)


# ── Health check ──
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "SinAI Backend",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
