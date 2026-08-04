# SinAI — SinhalaJournal-LLM

> **R26-SE-037** · *A Style-Controlled Large Language Model for Diverse Sri Lankan Newspaper Writing*
> An AI writing assistant for Sinhala journalism, built on **SinLlama** (Llama-3-8B extended for Sinhala, fine-tuned with per-task LoRA adapters) — grammar correction, headline generation, style rewriting, and news summarization, in Sinhala.

**🔴 Live app:** **[sinai.onrender.com](https://sinai.onrender.com/)**

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Component Status](#component-status)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

SinAI is a full-stack AI journalism assistant purpose-built for Sinhala. At its core is **SinLlama**, a Llama-3-8B checkpoint extended with a Sinhala tokenizer and fine-tuned separately for four editorial tasks via LoRA adapters, so each task gets a small, targeted adapter on a shared base model rather than one generalist model doing all four jobs badly:

| Tool | What it does | Model adapter |
|---|---|---|
| Grammar Checker | Fixes grammar, spelling, and punctuation while preserving meaning | `grammar_sinllama_v22` |
| Headline Generator | Writes engaging Sinhala headlines at short / medium / long word bands | `headline_sinllama_v19` |
| Style Rewriter | Rewrites articles in newspaper styles: formal, sports, youth, editorial, feature | `style_sinllama_v07` |
| News Summarizer | Abstractive summaries at short / medium / long lengths | `summarization_sinllama_v06` |

An **Optimize Article** flow chains all four in one pass — correct, headline, optionally restyle, optionally summarize — for the common case of taking a raw draft to publish-ready in one step.

The product ships to journalists through three surfaces: a **web app**, a **Chrome extension**, and a **Google Docs add-on**, all talking to the same backend API.

---

## Repository Structure

The project now spans four repositories. This repo (`R26-SE-037`) is the one submitted to the research panel; it also acts as a single entry point over the others via **git submodules**, so the whole project can be cloned and browsed from one place without merging separate histories or disturbing anyone's deploy integrations.

```
R26-SE-037/                    ← this repo (panel submission + container)
│
├── backend/                   ← original submitted implementation (FastAPI)
├── frontend/                  ← original submitted implementation (React)
├── data/, models/, scripts/   ← original data pipeline & training scripts
├── Scrappers/                 ← original news scrapers
├── docs/                      ← project documentation
│
├── SinAI-Training/            ← [submodule] → github.com/wahallu/SinAI-Training
│                                  Active model training & fine-tuning, GPU server
│
├── SinhalaJournalLLM/         ← [submodule] → github.com/wahallu/SinhalaJournalLLM
│                                  Active product: backend-api, web-app, Chrome
│                                  extension, Docs add-on — deployed to Render
│
└── manual-dataset/            ← [submodule] → github.com/nisalfonseka/
                                   SinahalaJournalLLM-Sinhala-grammar-corrector-component
                                   Hand-curated grammar correction dataset & evals
```

**`backend/`, `frontend/`, `data/`, `models/`, `scripts/`, `Scrappers/`** are this repo's own tracked content — the implementation as submitted to the panel. Work has continued since in the three linked repos below, which is where the current, deployed system actually lives.

### Cloning with submodules

```bash
git clone --recurse-submodules https://github.com/nisalfonseka/R26-SE-037.git

# already cloned without the flag?
git submodule update --init --recursive
```

### Keeping submodules current

The submodule pointers are pinned to a commit, not a moving branch — they don't update automatically when the linked repos get new commits.

```bash
git submodule update --remote --merge   # pull latest on each submodule's default branch
git add SinAI-Training SinhalaJournalLLM manual-dataset
git commit -m "Sync submodules"
```

---

## Component Status

### 🚀 SinhalaJournalLLM — the live product

Deployed and running at **[sinai.onrender.com](https://sinai.onrender.com/)** (frontend + backend, both on Render).

- **`apps/backend-api`** — FastAPI service behind all four tools plus `Optimize`, self-hosted authentication (own JWT issuance, no third-party auth dependency), per-user history, and an admin dashboard API (users, categories, runtime settings, token-usage analytics, audit activity).
- **`apps/web-app`** — React 19 + Vite + Tailwind SPA: the four tools, Optimize Article, dashboard, history, settings, and an `/admin` console.
- **`apps/chrome-extension`** — Manifest V3 extension (popup + inline assistant + context menus) for correcting text anywhere in the browser.
- **`apps/docs-addon`** — Google Docs sidebar (Apps Script) that calls the backend server-side.
- Every inference request goes through a provider chain — **SinLlama (GPU) → OpenRouter (hosted fallback) → mock** — so the product degrades gracefully instead of failing outright if the GPU box is down; responses report which provider actually served them.

### 🧠 SinAI-Training — model training

Fine-tunes SinLlama's per-task LoRA adapters and serves them via `serve_sinai.py` on a GPU box (single NVIDIA A40).

| Adapter | Status | Result |
|---|---|---|
| Grammar `v22` | **Deployed** | 87.7% stage2 / 80.0% stage3 / 75.0% stage4 accuracy, 6.7% over-correction. `v23` (trained on 6x the data) tested worse on the newest, hardest eval and was not promoted — see [manual-dataset](manual-dataset/) below |
| Headline `v19` | **Ready to deploy** | Artifact rate cut ~10× (11.2% → 1.1%) vs v18, in-band rate flat (79.7%) |
| Style `v07` | **Deployed** | 5 newspaper styles: formal, sports, youth, editorial, feature |
| Summarizer `v06` | **Deployed** | Length-conditioned (short/medium/long), replacing a fixed-length prompt |

Full run-by-run rationale (completion-only loss, LoRA on MLP not just attention, length-conditioning, artifact cleaning) is in that repo's `train_roadmap.md` and `CLAUDE.md`.

### 📚 manual-dataset — grammar training data

The hand-curated dataset behind the grammar adapter, organized one file per grammar rule (spelling, SOV order, passive/formal register, plural agreement, negation, numerals, sandhi, honorifics, and 10 more) so a specific failure mode can be fixed without disturbing the rest.

- **~4,900 rows** across 18 category files, merged/deduplicated into `cleaned_v6.jsonl` (5,532 rows, built and awaiting its training run).
- **Four held-out eval sets**: `stage2` (57 sentences), `stage3` (10 paragraphs), `stage4` (36 paragraphs from real news), `stage5` (51 cases from 4 more real articles, none of whose corrections overlap the training data — the hardest set, and where change-needed accuracy still tops out around 16% for every version tested).
- Explicitly measures and optimizes for **over-correction rate**, not just accuracy — a model that "fixes" already-correct text is worse than useless to an editor.

### 📦 R26-SE-037 (this repo) — original submission

The `backend/`, `frontend/`, `data/`, `models/`, `scripts/`, and `Scrappers/` folders are the implementation as it stood when submitted to the research panel — an earlier, self-contained snapshot of the same idea. They're kept as-is for the record; new work happens in the three repos above.

---

## Architecture

```
                    Chrome ext ──┐
                    Docs add-on ─┼─→  backend-api  ──→  model gateway
                    web-app ─────┘   (FastAPI,          (chain, first
                                      self-hosted         healthy wins)
                                      JWT auth)                │
                                        │            ┌─────────┼──────────┐
                                        ▼            ▼         ▼          ▼
                                   PostgreSQL   SinLlama   OpenRouter    mock
                                  (history,     (GPU box,   (hosted      (offline,
                                   users,        adapters   fallback)     rule-based)
                                   admin/audit)  v18/v19/
                                                 v07/v06)
```

- **web-app**, the **Chrome extension**, and the **Docs add-on** all call the same `backend-api`; the four writing tools also accept anonymous requests (rate-limited by IP, not persisted) so the extension and add-on don't need a login flow.
- **backend-api** owns auth (its own JWT issuance — no third-party auth service), per-user history, and the admin dashboard API, and is what's actually deployed at [sinai.onrender.com](https://sinai.onrender.com/).
- **Model gateway** tries SinLlama on the GPU box first, falls back to OpenRouter, then a rule-based mock — every response reports which provider actually served it.

---

## Features

- 🔤 **Grammar Checker** — corrected text plus a per-correction breakdown (position, original, corrected, rule applied)
- 📰 **Headline Generator** — ranked candidates at short/medium/long word bands, with out-of-band regeneration and trimming as a hard guarantee
- ✍️ **Style Rewriter** — formal, sports, youth, editorial, feature
- 📋 **News Summarizer** — short/medium/long abstractive summaries
- ⚡ **Optimize Article** — runs grammar → headline → optional restyle → optional summary in one pass
- 📊 **Dashboard & History** — unified activity feed across all tools, per-user
- 🛠️ **Admin console** — users, categories, runtime settings, token-usage analytics, audit log
- 🧩 **Chrome extension** and **Google Docs add-on** — the same tools, without leaving the page you're writing in

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy (async) + asyncpg, PostgreSQL, Pydantic v2, httpx |
| Frontend | React 19, Vite, Tailwind CSS 4, Radix UI, Lucide icons |
| Model training | Unsloth + TRL `SFTTrainer`, LoRA fine-tuning on Llama-3-8B, 4-bit quantization |
| Inference serving | FastAPI (`serve_sinai.py`), PEFT multi-adapter switching on a shared merged base |
| Auth | Self-hosted JWT (own issuance, no third-party auth dependency) |
| Deployment | Render (backend-api + web-app), GPU box for model serving |
| Browser/Docs clients | Chrome Manifest V3, Google Apps Script |

---

## API Reference

All endpoints are served by `backend-api` (the same service running at `sinai.onrender.com`).

| Endpoint | Method | Purpose |
|---|---|---|
| `/grammar/check` | POST | `{text}` → corrected text + word-level corrections |
| `/grammar/history`, `/grammar/{id}` | GET | Correction history |
| `/headlines/generate` | POST | `{text, count, category, length}` → ranked candidates in the requested word band |
| `/headlines/history` | GET | Generation history |
| `/rewrite` | POST | `{text, tone}` → rewrite in a trained style |
| `/rewrite/history` | GET | Rewrite history |
| `/summarize` | POST | `{text, length}` → short/medium/long summary |
| `/summarize/history` | GET | Summary history |
| `/history` | GET | Unified newest-first activity across all tools |
| `/meta` | GET | Supported tasks, styles, lengths, provider status, feature flags |
| `/health`, `/health/model` | GET | Liveness / model gateway status |
| `/admin/*` | various | Admin dashboard API (requires an admin account) |

The four writing-tool endpoints accept anonymous requests (rate-limited by IP, results not saved); `/*/history` and `/admin/*` require a session.

---

## Getting Started

Each submodule owns its own setup instructions — they're the source of truth and change independently of this file:

- **Product (backend-api / web-app / extension / docs add-on):** [`SinhalaJournalLLM/README.md`](SinhalaJournalLLM/README.md)
- **Model training / inference server:** [`SinAI-Training/CLAUDE.md`](SinAI-Training/CLAUDE.md)
- **Grammar dataset & eval scripts:** [`manual-dataset/README.md`](manual-dataset/README.md)
- **This repo's original submitted implementation:** see [`backend/`](backend/) and [`frontend/`](frontend/) — setup is the standard `pip install -r requirements.txt` / `npm install` for a FastAPI + Vite app.

For just trying the product, no setup is needed — it's live at **[sinai.onrender.com](https://sinai.onrender.com/)**.

---

## Roadmap

- **Grammar:** diagnose why `v23` (trained on 6x `v18`'s data, including a round targeted at the exact gap) still lost ground on `stage5` — the priority over adding further data volume; work through the pending native-speaker KEEP/DENY calls in `downgrade_audit.md` before the next corpus-driven normalization pass.
- **Headline:** deploy `v19` in production (currently `v18`) — the inference server needs a restart to pick it up.
- **Dataset:** resolve the known `stage2`/`stage3` labeling contradiction around නිල/නිළ agreement.
- **Product:** continue building out the admin analytics surface and strengthening the Chrome extension / Docs add-on parity with the web app.

---

## Contributing

1. Fork the relevant repository (product changes go to `SinhalaJournalLLM`, training changes to `SinAI-Training`, dataset changes to `manual-dataset`)
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`)
4. Open a Pull Request against that repo
5. If the change should be reflected here, bump the submodule pointer in `R26-SE-037` (see [Keeping submodules current](#keeping-submodules-current))

---

## License

This project is developed as part of **Research Project R26-SE-037**. All rights reserved.
