# SinAI — Sinhala Journalism LLM Workstation

> **R26-SE-037** · An AI-powered journalism workstation built for Sinhala language journalists, combining a fine-tuned LLM (SinLLaMA) with OpenRouter-backed cloud inference to deliver grammar correction, headline generation, style rewriting, and news summarization — all in Sinhala.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [API Reference](#api-reference)
- [Data Pipeline](#data-pipeline)
- [ML Models](#ml-models)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Overview

SinAI is a full-stack, production-grade AI journalism assistant tailored for the Sinhala language. It provides a professional 3-panel web interface that newsroom journalists can use to:

- **Correct grammatical errors** in Sinhala text with per-character correction details
- **Generate multiple headline candidates** from a full article using a multi-stage validation pipeline
- **Rewrite articles** in different tones (formal, casual, persuasive, academic, dramatic)
- **Summarize long-form news** into short, medium, or long summaries
- **Interact with SinLLaMA**, a custom fine-tuned Sinhala language model

All AI responses are persisted to a PostgreSQL database for history tracking and analytics. The backend is built on FastAPI with full async support, and the frontend is a React + Vite + TailwindCSS 4 SPA.

---

## Features

### 🔤 Grammar Checker
- Sends Sinhala text to the LLM with a structured prompt
- Returns the fully corrected text along with a **detailed list of corrections** (position, original fragment, corrected fragment, grammar rule applied)
- Handles verb endings (e.g., `යනව` → `යනවා`), particles, spelling, spacing, and punctuation
- Persists every check to PostgreSQL with paginated history retrieval

### 📰 Headline Generator
- **6-stage generation pipeline**: Preprocessing → Entity Extraction → Style-Conditioned Generation → Optimization → Validation (with auto-regeneration) → Semantic Extraction
- Supports multiple headline styles: **formal**, **breaking news**, **feature**, **digital**
- Returns the best headline, all ranked candidates with validation metrics, and a full pipeline execution log
- Integrated **AI news image generation** via ModelsLab API (with OpenRouter fallback)
- Semantic alignment scoring for generated images

### ✍️ Style Rewriter
- Rewrites Sinhala articles into different tones: Formal, Casual, Persuasive, Academic, Dramatic
- Preserves the original meaning while adjusting register and vocabulary
- Full history with pagination

### 📋 News Summarizer
- Summarizes long-form Sinhala articles
- Three length preferences: **Short**, **Medium**, **Long**
- Returns a clean summary in Sinhala
- Full history with pagination

### 🤖 SinLLaMA Integration
- Dedicated page for interacting with SinLLaMA — a custom fine-tuned Sinhala LLM
- Loaded via a local model loader (`sinllama_loader.py`)

### 📊 Dashboard & History
- Full session history stored in browser localStorage
- Filterable history by tool (grammar, headline, rewriter, summarizer)
- Copy-to-clipboard support on all outputs

### 👤 User Management
- Profile page, Settings page, Plans/Subscription page
- Configurable tone, summary length, headline style, max headline length, and candidate count

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend (Vite)                    │
│  Dashboard │ Grammar │ Headlines │ Rewriter │ Summarizer │ SinLLaMA │
│            └──────────────────────────────────────────────────  │
│                     src/services/api.js (fetch)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST  (CORS-enabled)
                           │ https://sinai.onrender.com/api/v1
┌──────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend (Uvicorn)                   │
│                                                                 │
│   /api/v1/grammar/*    /api/v1/headline/*                       │
│   /api/v1/style/*      /api/v1/summarize/*                      │
│                                                                 │
│   Services Layer:  grammar_service │ headline_service           │
│                    style_service   │ summarizer_service         │
│                                                                 │
│   Core:  openrouter_client.py  (async httpx, retry w/ backoff)  │
│          config.py (pydantic-settings)                          │
│          database.py (SQLAlchemy asyncio)                       │
└────────┬──────────────────────┬───────────────────────────────--┘
         │                      │
    ┌────▼────┐          ┌──────▼───────┐
    │PostgreSQL│          │ OpenRouter   │
    │(Render) │          │  LLM API     │
    └─────────┘          │ + ModelsLab  │
                         │ Image API    │
                         └──────────────┘
```

---

## Project Structure

```
R26-SE-037/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── main.py                 # App entrypoint, CORS, lifespan, routers
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py     # Aggregates all routers under /api/v1
│   │   │       ├── grammar.py      # Grammar check endpoints
│   │   │       ├── headline.py     # Headline generation + image endpoints
│   │   │       ├── style.py        # Style rewriter endpoints
│   │   │       └── summarize.py    # News summarizer endpoints
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic-settings configuration
│   │   │   ├── database.py         # Async SQLAlchemy engine + session
│   │   │   └── openrouter_client.py# Shared async LLM + image gen client
│   │   ├── models/                 # SQLAlchemy ORM models (PostgreSQL)
│   │   │   ├── grammar.py          # GrammarCorrection table
│   │   │   ├── headline.py         # HeadlineGeneration table
│   │   │   ├── style.py            # StyleRewrite table
│   │   │   └── summarization.py    # Summarization table
│   │   ├── repositories/           # Async DB CRUD operations
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── services/               # Business logic
│   │   │   ├── grammar/
│   │   │   │   ├── grammar_service.py   # LLM grammar correction
│   │   │   │   └── grammar_rules.py     # Rule-based pre/post processing
│   │   │   ├── headline/
│   │   │   │   └── headline_service.py  # 6-stage headline pipeline
│   │   │   ├── style/
│   │   │   └── summarizer/
│   │   └── preprocessing/          # Text preprocessing utilities
│   ├── tests/
│   │   └── test_grammar.py         # Async pytest test suite
│   └── requirements.txt
│
├── frontend/
│   ├── web-app/                    # React + Vite SPA
│   │   ├── src/
│   │   │   ├── App.jsx             # Root component + routing logic
│   │   │   ├── components/
│   │   │   │   ├── Sidebar.jsx     # Collapsible navigation sidebar
│   │   │   │   ├── Dashboard.jsx   # Home/landing dashboard
│   │   │   │   ├── InputBox.jsx    # Sinhala text input
│   │   │   │   ├── OutputPanel.jsx # Generic output display
│   │   │   │   ├── HeadlineOutputPanel.jsx  # Headline-specific output
│   │   │   │   ├── RightPanel.jsx  # Settings / config panel
│   │   │   │   ├── DotField.jsx    # Animated background overlay
│   │   │   │   ├── HistoryPage.jsx # Tool history browser
│   │   │   │   ├── ProfilePage.jsx # User profile
│   │   │   │   ├── SettingsPage.jsx# App settings
│   │   │   │   ├── Plans.jsx       # Subscription plans
│   │   │   │   ├── SinLLamaPage.jsx# SinLLaMA model interface
│   │   │   │   └── ToolHeader.jsx  # Per-tool title/description
│   │   │   ├── hooks/
│   │   │   │   └── useToolProcessor.js  # Shared async tool processing hook
│   │   │   ├── services/
│   │   │   │   └── api.js          # All backend API calls
│   │   │   ├── styles/             # Component-specific styles
│   │   │   └── index.css           # Global design system / tokens
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── browser-extension/          # (Planned) Browser extension
│   └── docs-integration/           # (Planned) Docs platform plugin
│
├── models/
│   ├── sinllama/                   # SinLLaMA base model artifacts
│   └── fine_tuned/                 # Fine-tuned model checkpoints
│
├── scripts/
│   ├── train/
│   │   ├── train_grammer.py        # Grammar correction fine-tuning script
│   │   └── train_summarizer.py     # Summarizer fine-tuning script
│   └── preprocess/
│       └── clean_data.py           # Dataset cleaning & deduplication
│
├── data/
│   ├── raw/                        # Raw scraped news corpora
│   ├── processed/                  # Cleaned & tokenized datasets
│   └── datasets/                   # JSONL training datasets
│
├── Scrappers/                      # News site scrapers
│   ├── Ada derana/
│   │   └── sinhala_adaderana_scraper.py
│   ├── ITN/
│   ├── vidusara/
│   └── hiru_mawbima_vikalpa/
│
├── docs/                           # Project documentation
├── .env                            # Environment variables (do NOT commit)
├── .gitignore
└── README.md
```

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| Framework | FastAPI ≥ 0.115 |
| ASGI Server | Uvicorn ≥ 0.34 |
| ORM | SQLAlchemy ≥ 2.0 (asyncio) |
| Database Driver | asyncpg ≥ 0.30 |
| Database | PostgreSQL (hosted on Render) |
| Migrations | Alembic ≥ 1.15 |
| Validation | Pydantic v2 + pydantic-settings |
| HTTP Client | httpx ≥ 0.28 (async) |
| LLM Gateway | OpenRouter API (OpenAI-compatible) |
| Image Gen | ModelsLab API + OpenRouter fallback |
| Testing | pytest ≥ 8.0 + pytest-asyncio |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 19 |
| Build Tool | Vite 8 |
| Styling | TailwindCSS 4 |
| UI Components | shadcn/ui + Radix UI |
| Icons | Lucide React |
| Typography | Geist (variable font) |
| Animation | tw-animate-css |
| Utilities | clsx + tailwind-merge + class-variance-authority |

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info and version |
| `GET` | `/health` | Health status check |

### Grammar Checker

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/grammar/check` | Check and correct Sinhala grammar |
| `GET` | `/grammar/history` | Paginated correction history |
| `GET` | `/grammar/{id}` | Single correction by UUID |

**POST `/grammar/check` — Request Body:**
```json
{
  "text": "මම ගෙදර යනව"
}
```

**Response:**
```json
{
  "id": "uuid",
  "corrected": "මම ගෙදර යනවා",
  "corrections": [
    {
      "position": 8,
      "original": "යනව",
      "corrected": "යනවා",
      "rule": "Verb ending requires final ා particle"
    }
  ],
  "correction_count": 1,
  "created_at": "2026-05-12T14:00:00Z"
}
```

### Headline Generator

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/headline/generate` | Generate headlines from an article |
| `POST` | `/headline/generate-image` | Generate a news image from a prompt |
| `GET` | `/headline/history` | Paginated generation history |
| `GET` | `/headline/{id}` | Single generation by UUID |

**POST `/headline/generate` — Request Body:**
```json
{
  "article_text": "...",
  "style": "formal",
  "max_length": 80,
  "num_candidates": 3
}
```

Supported styles: `formal`, `breaking`, `feature`, `digital`

### Style Rewriter

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/style/rewrite` | Rewrite text in a specified tone |
| `GET` | `/style/history` | Paginated rewrite history |

**Request Body:**
```json
{
  "text": "...",
  "tone": "formal"
}
```

Supported tones: `formal`, `casual`, `persuasive`, `academic`, `dramatic`

### News Summarizer

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/summarize/check` | Summarize a Sinhala news article |
| `GET` | `/summarize/history` | Paginated summarization history |
| `GET` | `/summarize/{id}` | Single summarization by UUID |

**Request Body:**
```json
{
  "text": "...",
  "length": "short"
}
```

Supported lengths: `short`, `medium`, `long`

> **Note:** Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` when running locally.

---

## Data Pipeline

SinAI includes a full data pipeline for building and maintaining Sinhala NLP training datasets.

### News Scrapers (`Scrappers/`)

Four dedicated scrapers collect raw Sinhala news articles:

| Scraper | Source |
|---|---|
| `sinhala_adaderana_scraper.py` | Ada Derana — සිංහල |
| ITN scraper | ITN — ශ්‍රී Lanka ITN |
| Vidusara scraper | Vidusara — Science & Tech |
| Hiru/Mawbima/Vikalpa scraper | Hiru News, Mawbima, Vikalpa |

### Preprocessing (`scripts/preprocess/`)

- `clean_data.py` — Removes duplicate entries and shuffles records to produce clean JSONL datasets, ready for fine-tuning.

### Data Directories (`data/`)

| Directory | Contents |
|---|---|
| `data/raw/` | Raw scraped news JSON/JSONL files |
| `data/processed/` | Cleaned, deduplicated, and tokenized data |
| `data/datasets/` | Final JSONL datasets used for training |

---

## ML Models

### SinLLaMA (`models/sinllama/`)

SinLLaMA is a custom **Sinhala-adapted LLM** fine-tuned from a base language model on Sinhala news corpora. It is optimized for:

- Grammatical error correction
- News summarization
- Sinhala text understanding

### Fine-Tuned Models (`models/fine_tuned/`)

Fine-tuned model checkpoints, adapted for specific journalism tasks:

| Script | Task |
|---|---|
| `scripts/train/train_grammer.py` | Grammar correction fine-tuning |
| `scripts/train/train_summarizer.py` | News summarization fine-tuning |

> Fine-tuning is performed on a GPU server (not locally). The trained model artifacts are exported to `models/fine_tuned/`.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- PostgreSQL database (or use the Render-hosted instance)
- OpenRouter API key — [openrouter.ai](https://openrouter.ai)

### Environment Variables

Create a `.env` file in the **project root** (same level as `backend/`):

```env
# ── Database ──
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<dbname>

# ── App ──
APP_ENV=development

# ── CORS (comma-separated origins) ──
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# ── OpenRouter ──
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openrouter/free

# ── Image Generation (optional) ──
# IMAGEGEN_API_KEY=<modelslab-key>
# IMAGEGEN_MODEL=<modelslab-model-id>
```

> ⚠️ **Never commit `.env` to version control.** It is already in `.gitignore`.

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to the web app directory
cd frontend/web-app

# Install dependencies
npm install

# Start the development server
npm run dev
```

The web app will be available at `http://localhost:5173`.

To point the frontend at a custom backend URL, set:

```env
# frontend/web-app/.env.local
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Running Tests

The backend test suite uses **pytest** with **pytest-asyncio** and **httpx** for async ASGI transport testing.

```bash
cd backend

# Activate your virtual environment first
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_grammar.py -v
```

### Test Coverage

| Test | Description |
|---|---|
| `test_root` | Verifies the health check endpoint returns `{"status": "ok"}` |
| `test_grammar_check_empty_text` | Ensures empty input is rejected with HTTP 422 |
| `test_grammar_check_valid_text` | Validates grammar correction on `"මම ගෙදර යනව"` → `"යනවා"` |

---

## Deployment

The backend is deployed on **Render.com** and is accessible at:

```
https://sinai.onrender.com
```

The frontend `api.js` defaults to the Render URL in production:

```js
const API_BASE = import.meta.env.VITE_API_BASE_URL
  || 'https://sinai.onrender.com/api/v1';
```

### Production Deployment Checklist

- [ ] Set `APP_ENV=production` in environment variables
- [ ] Configure `CORS_ORIGINS` to your exact frontend domain (no wildcards in production)
- [ ] Set `DATABASE_URL` to your production PostgreSQL connection string
- [ ] Set `OPENROUTER_API_KEY` to your production key
- [ ] Run `alembic upgrade head` on first deploy
- [ ] Build the frontend: `npm run build` in `frontend/web-app/`

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

### Code Conventions

- **Backend:** Follow PEP 8. Use type annotations throughout. All DB operations must be async.
- **Frontend:** Use functional React components with hooks. All API calls go through `src/services/api.js`.
- **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, `docs:`, `chore:`, etc.)

---

## License

This project is developed as part of **Research Project R26-SE-037**. All rights reserved.

---
