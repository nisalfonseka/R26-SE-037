# SinAI — SinhalaJournal-LLM

**Research project R26-SE-037 · Sri Lanka Institute of Information Technology**

SinAI is an AI-assisted writing system for Sinhala journalism. It provides four
editorial tools through a web application, Chrome extension, and Google Docs
add-on:

| Tool | Purpose |
|---|---|
| Grammar checker | Correct Sinhala grammar, spelling, and punctuation while preserving meaning |
| Headline generator | Generate short, medium, or long Sinhala headlines |
| Style rewriter | Rewrite an article in formal, sports, youth, editorial, or feature style |
| News summarizer | Produce short, medium, or long Sinhala summaries |

The system uses a shared SinLlama base model with a separate LoRA adapter for
each task. A FastAPI model gateway can use the research GPU server, a configured
hosted fallback, or a deterministic mock provider for local development.

> SinAI is research software. Review generated text before publication,
> especially names, quotations, numbers, and factual claims.

## Quick links

- **Research website:** [sin-ai.app](https://sin-ai.app/)
- **Try the web application:** [chat.sin-ai.app](https://chat.sin-ai.app/)
- **API health:** [backend.sin-ai.app/health](https://backend.sin-ai.app/health)
- **API capabilities:** [backend.sin-ai.app/api/v1/meta](https://backend.sin-ai.app/api/v1/meta)
- **Detailed project summary:** [FullSummary.md](FullSummary.md)
- **Questions and bug reports:** [GitHub Issues](https://github.com/nisalfonseka/R26-SE-037/issues)

## Contents

- [Start here](#start-here)
- [Repository structure](#repository-structure)
- [Clone the complete project](#clone-the-complete-project)
- [Frontend-only development](#frontend-only-development)
- [Full local development](#full-local-development)
- [Try the API directly](#try-the-api-directly)
- [Model training and GPU inference](#model-training-and-gpu-inference)
- [Grammar datasets and evaluation](#grammar-datasets-and-evaluation)
- [Tests](#tests)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Citation and use](#citation-and-use)

## Start here

Choose the path that matches what you want to do:

| Goal | Recommended path |
|---|---|
| Try SinAI without installing anything | Open the [live web application](https://chat.sin-ai.app/) |
| Work on the React interface | Follow [Frontend-only development](#frontend-only-development) |
| Run the API and web app locally | Follow [Full local development](#full-local-development) |
| Explore or train the language models | Read [Model training and GPU inference](#model-training-and-gpu-inference) |
| Inspect the grammar datasets and evaluations | Open [`manual-dataset/`](manual-dataset/) |
| Read the original submitted prototype | Open [`Initial work/`](Initial%20work/) |

## Repository structure

This repository is the public entry point for the research project. The active
product, model-training workspace, and grammar dataset retain their own Git
histories and are included here as submodules.

```text
R26-SE-037/
├── README.md
├── FullSummary.md              # detailed technical and research summary
├── Initial work/               # original self-contained submission snapshot
├── SinAI-Training/             # model training, evaluation, and GPU inference
├── SinhalaJournalLLM/          # active product and deployment code
└── manual-dataset/             # grammar datasets, audits, and evaluation tools
```

| Directory | Upstream repository | Main contents |
|---|---|---|
| [`SinhalaJournalLLM/`](SinhalaJournalLLM/) | [wahallu/SinhalaJournalLLM](https://github.com/wahallu/SinhalaJournalLLM) | FastAPI backend, React web app, Chrome extension, Docs add-on, portfolio, infrastructure |
| [`SinAI-Training/`](SinAI-Training/) | [wahallu/SinAI-Training](https://github.com/wahallu/SinAI-Training) | SinLlama setup, LoRA training, evaluation scripts, GPU inference server |
| [`manual-dataset/`](manual-dataset/) | [nisalfonseka/SinahalaJournalLLM-Sinhala-grammar-corrector-component](https://github.com/nisalfonseka/SinahalaJournalLLM-Sinhala-grammar-corrector-component) | Curated grammar data, held-out tests, audit scripts, experiment records |
| [`Initial work/`](Initial%20work/) | This repository | Earlier backend, frontend, data pipeline, models, and scrapers retained for research history |

The submodule commits recorded by this repository are the reproducible project
snapshot. The upstream repositories can move ahead independently.

## Clone the complete project

Clone with submodules so the three linked repositories are populated:

```bash
git clone --recurse-submodules https://github.com/nisalfonseka/R26-SE-037.git
cd R26-SE-037
```

If you already cloned the repository and the submodule folders are empty:

```bash
git submodule update --init --recursive
```

To restore every submodule to the exact version recorded by this repository:

```bash
git submodule update --init --recursive --checkout
```

## System overview

```text
Web app ───────────┐
Chrome extension ──┼──> FastAPI backend ──> model gateway ──> SinLlama GPU
Google Docs add-on ┘          │                    ├────────> hosted fallback
                              │                    └────────> mock provider
                              v
                       Supabase Postgres
                   auth, history, plans, audit data
```

- `apps/backend-api` is the common API for every client.
- `apps/web-app` is the main React workspace.
- The model gateway reports which inference provider served a request.
- Anonymous tool requests are supported but rate-limited and are not stored in
  personal history.
- Signed-in users can reopen saved work; administrators have separate
  management and research-diagnostics routes.

## Prerequisites

Only install what your chosen path needs:

| Purpose | Requirement |
|---|---|
| Clone the complete repository | Git with submodule support |
| Run the web application | Node.js 20+ and npm |
| Run the backend | Python 3.12 and a Supabase project |
| Run with containers | Docker with Compose v2 |
| Run the real SinLlama models | Linux, an NVIDIA CUDA GPU, model access, and substantial local storage |

The real model weights and trained task-adapter folders are intentionally not
stored in this Git repository. The frontend and backend can still be developed
with the mock provider.

## Frontend-only development

This is the quickest local setup. It runs the current React interface and uses
the public SinAI API by default, so no local Python environment or model weights
are required.

```bash
cd SinhalaJournalLLM/apps/web-app
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

Useful checks:

```bash
npm test
npm run lint
npm run build
```

The public service is shared and rate-limited. Use a local backend when changing
API behaviour or running repeated tests.

## Full local development

The easiest full-stack development mode uses Supabase for PostgreSQL and auth
data, the FastAPI backend locally, and `MODEL_PROVIDER=mock`. This exercises the
application without downloading the multi-gigabyte model stack.

### 1. Prepare Supabase

Create a development Supabase project. Do not use production credentials for
local experiments.

In the Supabase SQL editor:

1. Run [`apps/backend-api/schema.sql`](SinhalaJournalLLM/apps/backend-api/schema.sql).
2. Run every file in [`apps/backend-api/migrations/`](SinhalaJournalLLM/apps/backend-api/migrations/) in filename order.
3. Only if you need an administrator account, review
   [`apps/backend-api/scripts/seed_admin.sql`](SinhalaJournalLLM/apps/backend-api/scripts/seed_admin.sql)
   before running it.

Read the header comments in each migration before running it. Many migrations
are additive and idempotent, but the self-hosted-auth migration is a one-time
operation that rewrites user-related foreign keys. Take a database backup before
running migrations against an existing environment.

### 2. Configure and start the backend

```bash
cd SinhalaJournalLLM/apps/backend-api
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Set at least these values in `apps/backend-api/.env`:

```dotenv
PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVER_ONLY_SERVICE_ROLE_KEY
JWT_SECRET=YOUR_LONG_RANDOM_SECRET
IP_HASH_SALT=ANOTHER_LONG_RANDOM_SECRET
MODEL_PROVIDER=mock
MODEL_FALLBACK=true
APP_ENV=development
APP_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173
```

Generate secrets locally rather than reusing passwords:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/meta
```

Interactive API documentation is available at
[http://localhost:8000/docs](http://localhost:8000/docs).

Never expose `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, provider API keys, or
SMTP credentials in browser code, screenshots, issues, or commits.

### 3. Start the web application

In a second terminal:

```bash
cd SinhalaJournalLLM/apps/web-app
npm ci
npm run dev
```

Open [http://localhost:5173](http://localhost:5173), then set the API Base URL
in the app's Settings page to:

```text
http://localhost:8000/api/v1
```

### 4. Optional Docker Compose workflow

After creating `apps/backend-api/.env`, run from `SinhalaJournalLLM/`:

```bash
docker compose -f infra/docker-compose.yml up
```

The frontend is exposed on port `5173` and the backend on port `8000`. If the
frontend still targets the public API, set its API Base URL to the local URL in
the Settings page.

## Try the API directly

The liveness and capability endpoints do not require authentication:

```bash
curl https://backend.sin-ai.app/health
curl https://backend.sin-ai.app/api/v1/meta
```

The four main writing endpoints are available under `/api/v1`:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/grammar/check` | Grammar and spelling correction |
| `POST` | `/headlines/generate` | Controlled-length headline generation |
| `POST` | `/rewrite` | Newspaper-style rewriting |
| `POST` | `/summarize` | Controlled-length summarization |
| `POST` | `/optimize` | Combined editorial workflow |
| `GET` | `/meta` | Supported tasks, styles, lengths, and provider status |

Example anonymous grammar request:

```bash
curl -X POST https://backend.sin-ai.app/api/v1/grammar/check \
  -H 'Content-Type: application/json' \
  -d '{"text":"මෙහි පරීක්ෂා කිරීමට අවශ්‍ය සිංහල පාඨය යොදන්න."}'
```

Anonymous use is rate-limited. See the local Swagger documentation for the
complete request and response schemas.

## Model training and GPU inference

The model workspace is [`SinAI-Training/`](SinAI-Training/). Its scripts cover
base-model preparation, LoRA fine-tuning, evaluation, and multi-adapter serving.

Important limitations before starting:

- The task-adapter weights are not committed to Git.
- The initial download script obtains the Llama base, SinLlama adapter, and
  extended tokenizer; task adapters must be trained or supplied separately.
- Several research scripts contain paths from the original GPU server. Review
  and change them for your environment before running.
- Training and real inference require CUDA-compatible hardware. The research
  environment used an NVIDIA A40; requirements vary by task and configuration.

Initial model preparation:

```bash
cd SinAI-Training/work/sinllama
python download_model.py
python prepare_sinllama_base.py
```

Update the absolute path constants in `prepare_sinllama_base.py` before running
it outside the original research server.

Run the inference service from the `work` directory because its imports are
relative to that location:

```bash
cd ..
uvicorn serve_sinai:app --host 0.0.0.0 --port 8001
```

Then configure the product backend:

```dotenv
MODEL_PROVIDER=sinllama
SINLLAMA_API_URL=http://localhost:8001
MODEL_FALLBACK=true
```

Before training, read [`SinAI-Training/CLAUDE.md`](SinAI-Training/CLAUDE.md).
It documents the active scripts, prompt formats, adapter discovery, 4-bit
loading constraints, and known environment-specific paths.

## Grammar datasets and evaluation

The grammar component lives in [`manual-dataset/`](manual-dataset/). It contains
rule-organized JSONL data, merged training sets, held-out evaluations, audit
tools, and experiment reports.

Start with:

- [`manual-dataset/README.md`](manual-dataset/README.md) — dataset design and usage
- [`manual-dataset/train_roadmap.md`](manual-dataset/train_roadmap.md) — experiment history and decisions
- [`manual-dataset/STAGE6_CREATION_AND_EVALUATION.md`](manual-dataset/STAGE6_CREATION_AND_EVALUATION.md) — Stage 6 creation and evaluation process

Dataset and evaluation caveats are part of the research record. Do not present
an automatic or model-assisted audit as human linguistic validation. Confirm
licensing and source-provenance requirements before redistributing derived
news text.

## Other clients

### Chrome extension

1. Open `chrome://extensions` in Chrome.
2. Enable **Developer mode**.
3. Choose **Load unpacked**.
4. Select `SinhalaJournalLLM/apps/chrome-extension/`.
5. Set the API Base URL in the extension settings if you are using a local backend.

### Google Docs add-on

```bash
cd SinhalaJournalLLM/apps/docs-addon
npm install -g @google/clasp
clasp login
clasp push
```

`clasp push` updates the Apps Script project configured in `.clasp.json`. Review
that project ID and use your own Apps Script project before pushing changes.

## Tests

Backend tests use fake Supabase clients and the mock provider, so they can run
without a GPU:

```bash
cd SinhalaJournalLLM/apps/backend-api
source .venv/bin/activate
python -m pytest tests/ -v
```

Frontend checks:

```bash
cd SinhalaJournalLLM/apps/web-app
npm test
npm run lint
npm run build
```

Training and dataset evaluations are task-specific. Use the commands documented
inside their repositories and keep generated model checkpoints, predictions,
private review sheets, and large experiment outputs out of ordinary Git commits.

## Troubleshooting

| Problem | What to check |
|---|---|
| Submodule directories are empty | Run `git submodule update --init --recursive` from the repository root |
| A submodule shows a detached HEAD | This is normal for a pinned snapshot; switch to that submodule's branch before contributing there |
| Frontend calls the public API instead of localhost | Change the API Base URL in the web app Settings page |
| Backend fails during startup | Confirm `PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are present in `apps/backend-api/.env` |
| `/health/ready` returns `503` | Check Supabase reachability and confirm the schema and migrations were applied |
| Output reports the `mock` provider | Set `MODEL_PROVIDER=sinllama` and verify `SINLLAMA_API_URL` if you intend to use the GPU model |
| Browser reports a CORS error | Add the exact frontend origin to `CORS_ORIGINS` and restart the backend |
| Model server cannot find adapters | The adapter folders are not bundled; train or copy them and update the local paths |
| Port already in use | Change the Uvicorn/Vite port and update the frontend API Base URL or CORS origin accordingly |

## Contributing

Make changes in the repository that owns the component:

- Product, APIs, web UI, browser extension, or Docs add-on →
  [`SinhalaJournalLLM`](https://github.com/wahallu/SinhalaJournalLLM)
- Training, inference, or task evaluation →
  [`SinAI-Training`](https://github.com/wahallu/SinAI-Training)
- Grammar datasets and dataset tooling →
  [`manual-dataset`](https://github.com/nisalfonseka/SinahalaJournalLLM-Sinhala-grammar-corrector-component)
- Project-level documentation or pinned submodule versions → this repository

Suggested workflow:

```bash
git switch -c feature/short-description
# make and test the change
git status
git commit -m "feat: describe the change"
git push -u origin feature/short-description
```

Please do not commit credentials, `.env` files, model checkpoints, private
review data, raw copyrighted corpora, generated prediction dumps, archives, or
operating-system files such as `.DS_Store`.

When reporting a problem, include the affected component, operating system,
Python or Node version, exact command, error output, and whether the request was
served by `sinllama`, a hosted provider, or `mock`. Remove secrets and personal
data first.

## Research team

| Member | Research component |
|---|---|
| Nisal Fonseka | Sinhala grammar correction and morphological error detection |
| Akash Jayasinghe | Controlled-length headline generation and visual synthesis |
| Chathushka Navod | Abstractive and extractive Sinhala news summarization |
| Sandun Hettiarachchi | Multi-publication editorial style adaptation and tone transfer |

Supervised by **Prof. Nuwan Kodagoda** with **Ms. Poojani Gunathilake** as
co-supervisor at the Faculty of Computing, SLIIT.

## Citation and use

If this repository supports academic work, cite the project and link to the
exact commit or release used so the software and submodule versions are
reproducible:

```text
SinAI Research & Engineering Group. (2026). SinhalaJournal-LLM:
A Style-Controlled Large Language Model for Diverse Sri Lankan Newspaper
Writing (Research Project R26-SE-037). https://github.com/nisalfonseka/R26-SE-037
```

This public repository currently does not include an open-source `LICENSE`
file. Public visibility alone does not grant permission to copy, redistribute,
or commercially use the code, datasets, model artifacts, or research content.
Contact the research team for permissions beyond inspection and academic
reference. Third-party models, news sources, libraries, and services retain
their own terms and licenses.
