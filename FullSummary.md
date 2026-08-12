# SinhalaJournal-LLM / SINAI Repository Research Audit

**Snapshot date:** 2026-08-12  
**Project ID:** R26-SE-037  
**Scope:** All repositories and research folders under `/Users/nisalfonseka/Documents/GitHub/Research`, including current source code, locally available datasets, experiment logs, documentation, configuration, and relevant Git history.

> **Evidence policy:** Saved experiment results and training logs take precedence over executable scripts, which take precedence over current dataset contents and Git history. README files are used for project identity and stated intent, but their model-version, architecture, and deployment claims are treated as historical or conflicting when newer source/results disagree.

No repository files were modified while performing the underlying audit. This document was subsequently created at the user's request.

## Repository snapshot and authority

| Repository | Audited revision/state | Research role |
|---|---|---|
| `SinAI-Training` | `86536dd55b40091eb86dc30ee9ac7254133d87ff` | Current model training, evaluation, and GPU inference code |
| `SinhalaJournalLLM` | Checked-out `e03ee23217e50e564957248a53d256c426d2295b`; two commits behind `origin/main` at audit time | Current SINAI application source |
| `manual dataset` | `e7cb04ec35ec653fe103e0a38f1547e1254d822a`, with pre-existing local changes | Grammar datasets, generation scripts, tests, and result logs |
| `R26-SE-037` | `a66fb47ddb9b8e92b1b679402635e7806260d40e` | Panel/umbrella repository and historical submitted snapshot |

The repositories embedded as `R26-SE-037` submodules duplicate the standalone repositories and are not independent experiments. The umbrella README itself identifies the linked repositories as the continuing work and its own older folders as the submitted snapshot (`README.md:43-68,124-126`).

The checked-out application did not include remote-only commit `324bb23`, which adds optional reference-image upload support. That feature is not treated as part of the audited working tree or as verified deployment.

---

# 1. Project overview

## Identity, problem, and objective

| Item | Verified finding | Evidence |
|---|---|---|
| Official project title | **SinhalaJournal-LLM: A Style-Controlled Large Language Model for Diverse Sri Lankan Newspaper Writing** | `README.md:1-4`; `SinhalaJournalLLM/README.md:1-5` |
| Product name | **SinAI**; this report uses “SINAI” descriptively | `README.md:1,26-39` |
| Project ID | **R26-SE-037** | `README.md:3` |
| Current purpose | A Sinhala journalism assistant for grammar correction, headline generation, style rewriting, and news summarization | `README.md:3-4,28-39` |
| Operational research problem | Adapting a Sinhala-extended Llama-3-8B to newsroom tasks while controlling correction restraint, writing style, headline length, and summary length | `README.md:28-39`; `SinAI-Training/CLAUDE.md:71-96` |
| Formal research question/hypothesis set | **NOT FOUND** |
| Target users | Journalists, journalism/media students, editors/sub-editors, researchers, and other users | `SinhalaJournalLLM/apps/backend-api/schema.sql:263-269` |
| Intended user-study population | University journalism students reached through a WhatsApp group | `SinhalaJournalLLM/apps/backend-api/app/core/research.py:1-8` |

## Research project versus application

- **SinhalaJournal-LLM** is the research/model umbrella: datasets, SinLLaMA adaptation, model experiments, and evaluation.
- **SinAI/SINAI** is the integrated product exposing those components through a web application, Chrome extension, and Google Docs add-on (`README.md:28-39,93-112`).
- Because the application repository is also named `SinhalaJournalLLM`, this is a conceptual distinction rather than a strict repository-name boundary.

## Major components and current completion

| Component | Implementation state | Experimental state | Deployment status |
|---|---|---|---|
| Grammar correction | Training/evaluation through v27; backend API, lexicon, chunking, and substitution warnings implemented | Strongest component evidence, with saved logs and current-gold results | Integrated; exact live adapter **NOT FOUND** |
| Summarization | mT5, extractive, and SinLLaMA v01-v07 scripts implemented | v06 is the latest version with a tracked result artifact; v07 is code/data cleaning only | Integrated; exact live adapter **NOT FOUND** |
| Style rewriting | Five-style generation, v07-v11 training history, serving/API implemented | No authoritative saved v11 evaluation | Integrated; exact live adapter **NOT FOUND** |
| Headline generation | v17-v20 trainers/evaluators and backend post-processing implemented | v18-v20 results documented; raw JSON absent; v19 retained as preferred experiment | Integrated; exact live adapter **NOT FOUND** |
| Shared model server | One quantized base with four PEFT adapters | Source complete | External adapter filesystem/runtime settings unavailable |
| Backend | FastAPI, self-hosted auth, persistence, telemetry, Optimize, admin APIs | Implemented | Hosting claimed, live revision **NOT FOUND** |
| Web app | Four tools, Optimize, history, onboarding, admin, media workflow | Implemented | Repository claims Render |
| Chrome extension | MV3 popup, inline assistant, context menus, auth/history | Implemented | Store publication **NOT FOUND** |
| Google Docs add-on | Sidebar, four tools, Optimize, auth/history | Implemented | Apps Script linkage exists; Marketplace publication **NOT FOUND** |
| User evaluation | Telemetry and external Google Form link | Completed study/results **NOT FOUND** | Instrumentation implemented |

## Originally proposed versus implemented

The historical submitted backend contains rule-based grammar and extractive headline placeholders explicitly intended to be replaced by SinLLaMA (`Initial work/backend/app/services/grammar/grammar_rules.py:1-9`; `Initial work/backend/app/services/headline/headline_generator.py:1-5`; `entity_extractor.py:1-5,68`).

The replacement was actually implemented as a common SinLLaMA foundation with task-specific LoRA adapters. A separate fine-tuned NER model mentioned by the historical placeholder is **NOT FOUND** in the current architecture.

---

# 2. Current system architecture

## Text architecture diagram

```text
Journalist / student / editor
        |
        +----------------------+-----------------------+
        |                      |                       |
 React 19 web app      Chrome MV3 extension   Google Docs add-on
        |                      |                       |
        +----------------------+-----------------------+
                               |
               JSON REST or streamed NDJSON
                 optional backend Bearer JWT
                               |
                               v
                 FastAPI backend /api/v1
                 - self-hosted JWT/bcrypt auth
                 - role checks and rate limiting
                 - preprocessing/post-processing
                 - task history and telemetry
                 - Optimize orchestration
                    |                    |
                    |                    +--> Supabase/PostgreSQL
                    |                         users, profiles, history,
                    |                         settings, telemetry, audit
                    |
                    +--> ModelGateway
                           |
                           +--> SinLLaMA GPU HTTP server
                           |      one 4-bit shared base
                           |      task-specific PEFT LoRAs
                           |
                           +--> OpenRouter hosted fallback
                           |
                           +--> deterministic mock fallback

Headline media path:
article + selected headline
    -> Groq English visual-prompt generation
    -> editable prompt
    -> admin-only OpenAI gpt-image-2
    -> optional Cloudinary storage/history
    -> web preview/download
```

Core evidence: `SinhalaJournalLLM/apps/backend-api/app/main.py:21-41`; `app/api/v1/__init__.py:7-38`; `app/core/model_gateway.py:44-46,78-181`; `SinAI-Training/work/serve_sinai.py:24-25,43-132,178-210`.

## Technology and service inventory

| Layer | Actual current implementation | Evidence |
|---|---|---|
| Frontend | React 19, Vite, Tailwind SPA | `SinhalaJournalLLM/apps/web-app/package.json:12-39` |
| Backend | FastAPI, Python 3.12 container | `apps/backend-api/app/main.py:21-41`; `Dockerfile:1-15` |
| Database | PostgreSQL through asynchronous Supabase/PostgREST client | `app/core/database.py:1-28`; `schema.sql:1-5` |
| Authentication | Backend-issued JWT, bcrypt passwords, refresh tokens, verification/reset tokens, optional Google ID-token exchange | `app/core/auth.py:1-16`; `security.py:64-150`; `api/v1/auth.py:133-365` |
| Authorization | Optional-user, required-user, and admin dependencies; roles loaded from `profiles` | `app/core/deps.py:43-115` |
| Model-serving layer | Separate FastAPI GPU service; backend calls `/generate` over HTTP | `app/models/sinllama_loader.py:1-18,34-98` |
| GPU model architecture | Shared `SinLLaMA-merged-base` with dynamically selected PEFT adapters | `SinAI-Training/work/serve_sinai.py:43-107,178-210` |
| Fallback chain | SinLLaMA -> OpenRouter -> mock | `app/core/model_gateway.py:78-181` |
| Durable queue | Redis, Celery, RabbitMQ, Kafka, or equivalent: **NOT FOUND** |
| Concurrency | `asyncio` fan-out for headlines/Optimize; process-local lock serializes adapter selection and generation | `headline_service.py:107-220`; `optimize_service.py:78-186`; `serve_sinai.py:543-565` |
| Caching | 30-second in-process runtime-settings TTL and in-process lexicon cache | `runtime_settings.py:1-12,24-69`; `grammar/lexicon.py` |
| Inference-result cache | **NOT FOUND** |
| Model storage | External `/home/jovyan/work/sinllama/models/...` filesystem | `serve_sinai.py:24-25` |
| External AI APIs | OpenRouter, Groq, OpenAI Images | `model_gateway.py`; `visual_prompt_service.py`; `image_generation_service.py` |
| External services | Supabase/PostgreSQL, Google OAuth, optional Cloudinary | `app/core/config.py:20-59`; `cloudinary_service.py:1-66` |

### Current code/documentation conflicts

- Current source uses backend-issued authentication, not Supabase Auth. The standalone README and old schema sections remain stale (`SinhalaJournalLLM/README.md:36-55,81-91`; `migrations/2026-08-02-self-hosted-auth.sql:1-19,36-150`).
- The umbrella README claims SQLAlchemy/asyncpg, but the current requirements and source use Supabase/PostgREST (`README.md:166-175`; `SinhalaJournalLLM/apps/backend-api/requirements.txt:1-14`; `app/core/database.py:1-28`).

## Actual task data flows

| Task | Verified flow |
|---|---|
| Grammar | Input -> sentence/paragraph chunks -> sequential model calls -> first-line sanitation -> word diff -> suspicious substitution checks -> advisory lexicon/end-form suggestions -> persistence (`grammar_service.py:181-309`) |
| Headline | Input/category/length -> concurrent candidate generation -> artifact removal -> out-of-band retries -> maximum-length trimming -> deduplication -> persistence (`headline_service.py:107-220`) |
| Style | Input/tone resolution -> model gateway -> output normalization -> persistence (`style_service.py:16-47`) |
| Summary | Input/length resolution -> model gateway -> output normalization -> persistence (`summarizer_service.py:16-46`) |
| Optimize | Grammar first -> optional style -> headline and optional summary concurrently -> streamed NDJSON; completed stages survive another stage's failure (`optimize_service.py:78-186`; `api/v1/optimize.py:58-145`) |

---

# 3. Grammar correction component

## Objective and implemented stack

The objective is to correct Sinhala grammar, spelling, and editorial errors while preserving already-correct text exactly. Restraint and over-correction are first-class requirements (`manual-dataset/README.md:1-10`; `README.md:118-122`).

Implemented stack:

- Llama-3-8B plus `polyglots/SinLlama_v01` and the extended Sinhala tokenizer, merged into `SinLLaMA-merged-base` (`SinAI-Training/work/sinllama/download_model.py:7-25`; `prepare_sinllama_base.py:9-38`).
- Supervised PEFT/LoRA with 4-bit base loading and completion-only loss from the successful v16 run onward (`train_grammar.py:199-304,449-475`).
- Backend chunking, sanitation, correction diffing, lexicon suggestions, sentence-final suggestions, and suspicious-substitution warnings (`grammar_service.py:87-148,181-310`).

Grammar-specific mT5 and ByT5 implementations are **NOT FOUND**. The mT5 code in `serve_sinai.py` applies to summarization. Historical rule code is a placeholder/mock, not an evaluated research baseline.

## Dataset schema

Current grammar JSONL records use:

```text
instruction: correction instruction
input:       possibly erroneous Sinhala text
output:      expected corrected text
```

`input != output` denotes correction-required; equality denotes a preservation/no-change control.

## Category datasets

Counts below come from direct parsing of current files in the standalone `manual dataset` repository.

| Dataset | Rows | Changed | Purpose |
|---|---:|---:|---|
| `Mixed.jsonl` | 341 | 336 | Multiple errors |
| `causative.jsonl` | 59 | 48 | Causatives |
| `copula.jsonl` | 76 | 49 | Copula |
| `correct.jsonl` | 780 | 0 | Clean controls |
| `correct_extra.jsonl` | 35 | 0 | Additional controls |
| `definiteness.jsonl` | 99 | 58 | Definiteness |
| `deixis.jsonl` | 42 | 28 | Deixis |
| `honorific.jsonl` | 76 | 58 | Honorific agreement |
| `involitive.jsonl` | 126 | 89 | Volitive/involitive |
| `negation.jsonl` | 111 | 79 | Negation |
| `numeral.jsonl` | 109 | 31 | Numeral correction/preservation |
| `paragraph.jsonl` | 98 | 89 | Paragraph correction |
| `passive.jsonl` | 334 | 248 | Passive/formal register |
| `plural.jsonl` | 249 | 229 | Plural agreement |
| `pronoun.jsonl` | 179 | 158 | Pronouns |
| `register.jsonl` | 249 | 16 | Mostly register-preservation controls |
| `sandhi.jsonl` | 104 | 90 | Joining/spacing |
| `sov.jsonl` | 378 | 369 | SOV order |
| `spelling.jsonl` | 853 | 796 | Confusable letters/vowel length |
| `verb.jsonl` | 191 | 180 | Tense/aspect/endings |
| `news_ai_grammar_dataset.jsonl` | 491 | 489 | AI-labelled/generated by filename; provider **NOT FOUND** |
| `news_ai_formal_dataset.jsonl` | 500 | 363 | Formal-news pairs; provider **NOT FOUND** |
| `news_correct.jsonl` | 398 | 23 | News preservation |
| `new_claude_v11_86_samples.jsonl` | 86 | 61 | Filename indicates Claude; procedure **NOT FOUND** |
| `new_claude_v12_50_samples.jsonl` | 50 | 34 | Same limitation |
| `new_claude_v13_63_samples.jsonl` | 63 | 46 | Same limitation |
| `final_corrected.jsonl` | 2,347 valid | 1,506 | Aggregate source; one malformed line |
| `stage5_round.jsonl` | 9,000 | 7,500 | Corpus-derived targeted corruption |

Category meanings and the lack of broad native-speaker review are documented in `manual dataset/README.md:123-165`.

## Merged training-set lineage

| Dataset | Rows | Changed | Unique exact records | Research use |
|---|---:|---:|---:|---|
| `cleaned.jsonl` | 2,316 | 1,488 | 2,316 | v13 |
| `cleaned_v2.jsonl` | 2,851 | 1,849 | 2,851 | v14 |
| `cleaned_v3.jsonl` | 3,709 | 2,402 | 3,709 | v16 |
| `cleaned_v4.jsonl` | 4,226 | 2,742 | 4,226 | v17 |
| `cleaned_v5.jsonl` | 4,423 | 2,834 | 4,423 | v18 |
| `cleaned_v6.jsonl` | 5,532 | 3,580 | 5,532 | v19/base handcrafted set |
| `cleaned_v7.jsonl` | 12,000 | 7,800 | 12,000 | Corpus generation |
| `cleaned_v7_full.jsonl` | 17,532 | 11,380 | 17,531 | v20/v21 |
| `cleaned_v8.jsonl` | 16,000 | 10,400 | 16,000 | Improved corruption set |
| `cleaned_v8_full.jsonl` | 27,064 | 17,560 | 21,532 | v22; includes oversampling |
| `cleaned_v9_full.jsonl` | 36,006 | 25,032 | 30,367 | v23/v24 |
| `cleaned_v10_full.jsonl` | 36,006 | 26,465 | 30,367 | v25-v27 |

Important data-quality conflicts:

- The README describes merged data as deduplicated, but the `*_full` sets intentionally oversample and contain thousands of duplicate records. `cleaned_v8_full` has 5,532 duplicate excess records; v9/v10 have 5,639 (`manual dataset/README.md:119-121`; `clean_and_shuffle.py:10-31`).
- Shuffling in `clean_and_shuffle.py:45-51` has no fixed seed.
- `cleaned_v7_report.md:3` says 16,000 rows, while the current `cleaned_v7.jsonl` has 12,000.
- Direct audit found residual non-NFC records in later merged datasets, so normalization is implemented but not perfect in persisted outputs.
- v10 preserves v9 inputs/order but changes 4,999 target rows, making 6,002 word corrections over 221 human-adjudicated spellings (`cleaned_v10_report.md:1-18`).

## Real-news corpus and corruption

| Corpus source | Rows | Location |
|---|---:|---|
| Ada Derana, including business | 214,944 | `manual dataset/New Dataset/derana 1/` through `derana 4/`, plus `derana business/` |
| ITN | 106,627 | `New Dataset/itn/`; merged `manual dataset/itn_merged.json` |
| Vidusara | 939 | `New Dataset/vidusara/` |
| Total raw records | 322,510 | Current local files; inventory logic in `New Dataset/count_articles.py` |

The news schema is `Category`, `Date`, `Headline`, `News Content`, `Source`, and `URL`.

The grammar builder performs NFC normalization, language/length filtering, 35% no-change allocation, three to eight corruptions, pair caps, and fixed seed 42 (`scripts/build_corpus_dataset.py:47-77,376-386,884-970`).

Implemented corruptions include ණ/න, ළ/ල, ෂ/ශ, vowel length, missing vowel signs, prenasalized consonants, ZWJ conjuncts, doubled letters, number and `වල` spacing, stray hal kirīma, verbs, quotatives, and SOV order (`:82-174,683-878`).

Valid/context-dependent twin forms including `කල/කළ`, `සිටි/සිටී`, and `නිල/නිළ` are protected through `AMBIGUOUS_KEEP` (`:266-289`). This is the clearest implemented spelling-versus-contextual-grammar distinction.

The current working copy of the builder has uncommitted linguistic corrections, including removal of an erroneous `සක්‍රීය -> සක්‍රිය` rule and addition of anusvara ministry forms. These changes were not inputs to completed v25-v27 experiments.

## v9/v10 construction and target quality

The 9,000-row stage5-focused round contains 2,500 verb-ending rows, 2,000 corrupted proper names, 1,500 name-preservation controls, and 3,000 long sparse-error rows (`cleaned_v9_report.md:1-19`; `scripts/build_stage5_round.py`).

A later audit identified suspected answer-side misspellings in 13.2% of v9 rows and 1,625 distinct suspect answer words (`train_roadmap.md:421-456`). v10 is the corresponding target-repair experiment; clearing the adjudicated list does not prove that every target is linguistically correct.

## Evaluation sets

| Test set | N | Correction/preserve | Character |
|---|---:|---:|---|
| `grammar_test_stage2.jsonl` | 57 | 42/15 | Single sentences |
| `grammar_test_stage3.jsonl` | 10 | 10/0 | Paragraphs; cannot measure restraint |
| `grammar_test_stage4.jsonl` | 36 | 26/10 | Four real-news articles |
| `grammar_test_stage5.jsonl` | 51 | 38/13 | Four different real-news articles |

Stage5 combines seven real published errors with injected orthographic, spacing, register, SOV, multi-error, and preservation cases (`stage5_manifest.md:1-35`; `scripts/build_stage5.py:154-236`).

Nine gold targets were later changed—two stage2, one stage3, two stage4, and four stage5—so older transcript summaries are not directly comparable without current-gold rescoring (`scripts/patch_gold_v10.py:1-80`).

## Grammar experiment chronology

Successful v16+ runs generally use the merged SinLLaMA base, 4-bit loading, maximum length 512, batch 2, gradient accumulation 4, LR `5e-5`, cosine scheduling, 10% warmup, a 5% random validation split, and completion-only SFT (`SinAI-Training/work/sinllama/scripts/train_grammar.py:199-255,328-345,449-475`).

| Version | Dataset | LoRA/objective/schedule | Verified result | Decision |
|---|---|---|---|---|
| v4 | Historical stage4 dataset | r16/α16 attention; max256; LR2e-4; 800 steps | Completed result **NOT FOUND** | Historical Git-only trainer |
| v5-v12 | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** |
| v13 | 2,316 | r16/α16 attention; 5 ep.; full-sequence loss | Stage2 49.1%; change 42.9%; preserve 66.7%; over 33.3% | Add data |
| v14 | 2,851 | Same | Identical to v13 | Investigate response masking |
| v15 | Planned completion-only isolation | Two failed TRL collator/API attempts | Validated adapter **NOT FOUND** | Repair trainer |
| v16 | 3,709 | r16 attention; completion-only; 5 ep. | Stage2 54.4%; stage3 40% | Add coverage |
| v17 | 4,226 | Same family | Stage2 64.9%; stage3 60%; over 26.7% | Add capacity/data |
| v18 | 4,423 | r32/α32 attention+MLP | Stage2 84.2%; stage3 70%; over 6.7% | Continue categories; capacity/data confounded |
| v19 | 5,532 | r32 attention+MLP | Stage2 93%; stage3 90%; stage4 58.3% | Test real-news generalization |
| v20 | 17,532 | r32; 5 ep. | Stage2 80.7%; stage3 70%; stage4 66.7%; stage5 37.3% | Repair/expand data |
| v21 | v20 plus ~80-row delta | Same family | Byte-identical to v20 | Build larger v8 set |
| v22 | 27,064 | r32; 4 ep. | English prompt: 87.7/80/75/33.3% across stages | Target stage5 gap |
| v23 | 36,006 v9 | r32; 4 ep. | Old-gold aggregate 61.0%; stage5 27.5% | Test schedule hypothesis |
| v24 | 36,006 v9 | r32; ~3.01 ep. | Current-gold 57.8%; unseen-pair 42% | Repair targets |
| v25 | 36,006 v10 | r32; 4 ep. | Current-gold 66.2%; unseen 50%; overtrained after epoch 3 | Stop at 3 epochs |
| v26 | 36,006 v10 | r32; 3 ep. | 65.6%; stage4 75%; unseen 47% | Test lower capacity |
| v27 | 36,006 v10 | **r4/α4**; 3 ep. | 66.9%; stage5 43.1%; unseen 48% | Lower rank did not improve transfer |
| v28+ | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** | **NOT FOUND** |

Key sources: `manual dataset/Tested_results/`; `train_roadmap.md`; `train_grammar.py`; `train_grammar_v27.py`.

## Latest authoritative grammar results

### Current-gold version comparison

| Version | Stage2 | Stage3 | Stage4 | Stage5 | Aggregate exact | Taught-pair | Untaught-pair |
|---|---:|---:|---:|---:|---:|---:|---:|
| v24 | 77.2% | 80.0% | 69.4% | 23.5% | 57.8% | 88% | 42% |
| v25 | 80.7% | 100% | 72.2% | 39.2% | 66.2% | 91% | **50%** |
| v26 | 78.9% | 100% | **75.0%** | 37.3% | 65.6% | 91% | 47% |
| v27 | 80.7% | 100% | 69.4% | **43.1%** | **66.9%** | 91% | 48% |

Evidence: `manual dataset/scripts/analyze_eval.py:111-203`; `Tested_results/results v24.md`; `v25 adapter stage 4.md`; `v26 adap reults.md`; `v27 results.md`.

### Detailed v27 evaluation

| Stage | Exact | Correction-needed | Preservation | Over-correction | ROUGE-L | GLEU | Char-F1 | Token F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Stage2 | 80.7% | 76.2% | 93.3% | 6.7% | .9856 | .9826 | .9934 | .9924 |
| Stage3 | 100% | 100% | n/a | n/a | 1.000 | 1.000 | 1.000 | 1.000 |
| Stage4 | 69.4% | 57.7% | 100% | 0% | .9911 | .9895 | .9968 | .9961 |
| Stage5 | 43.1% | 23.7% | 100% | 0% | .9817 | .9875 | .9964 | .9955 |

Evidence: `manual dataset/Tested_results/v27 results.md:366-382,449-465,689-705,1018-1048`.

Across all 154 examples, v27 achieves 103/154 = 66.9% exact match, 66/116 = 56.9% correction-needed exact accuracy, 37/38 = 97.4% preservation, and 1/38 = 2.6% over-correction.

Metric interpretation:

- Exact match requires the full predicted output to equal the target.
- Correction-needed accuracy is exact match restricted to erroneous inputs.
- Preservation and over-correction quantify restraint.
- Token precision/recall/F1 are grapheme-multiset overlap, not edit-level GEC metrics (`test_grammar.py:356-394`).
- Char-F1 ignores order and can be misleading for reordered text.
- ROUGE/GLEU are high even on some wrong long sentences because most characters are copied.
- Dedicated under-correction, F0.5, and edit-level precision/recall/F1 are **NOT FOUND**.
- Authoritative latency is **NOT FOUND**.

No single model dominates every criterion: v27 leads aggregate and stage5; v26 leads stage4; v25 leads measured untaught-pair transfer. Significance between 66.9% and 66.2% was not tested.

## Grammar failure modes

| Finding | Evidence |
|---|---|
| Exact-pair dependence | Older v22-v24 taught 68% vs untaught 26%, Fisher p=.0014 (`train_roadmap.md:25-58`); v25-v27 remain ~91% vs 47-50% |
| Copying/under-correction | 24 of v22's 34 stage5 failures returned input unchanged (`train_roadmap.md:298-301`) |
| More targeted data worsened results | v23 added 9,000 rows but aggregate/stage5 declined (`manual dataset/README.md:47-57`) |
| Bad targets | 13.2% of v9 rows triggered target audit (`train_roadmap.md:421-456`) |
| Over-training | v25 evaluation loss rose during epoch 4 (`v25 adapter training logs.md:11-21`) |
| Rank reduction did not improve transfer | v27 untaught 48%, below v25's 50% (`train_grammar_v27.py:274-287`) |
| Entity corruption | Surname substitutions and an estimated 1.5-2% factual alteration rate (`train_roadmap.md:460-483`) |
| Dense/long inputs | Partial fixes in five-to-six-error paragraphs (`train_roadmap.md:819-825`) |
| Context-valid spellings | Protected through `AMBIGUOUS_KEEP` (`build_corpus_dataset.py:266-289`) |
| Unicode/conjunct problems | ZWJ-loss/collapse corruption added following observed failures (`:94-130`) |
| Over-formalization/meaning changes | Documented in legal/control sentences (`train_roadmap.md:303-306`) |
| Broad unrelated-text hallucination | **NOT FOUND** as a documented grammar result |

## Current production grammar adapter

The exact production adapter is **NOT FOUND**.

Verified trace:

1. `grammar_service.py:219-224` calls `model_generate("grammar", ...)`.
2. Runtime settings may override `adapters.grammar`; blank means server default (`model_gateway.py:212-237`; `settings_registry.py:94-98`).
3. The backend posts to the GPU server (`sinllama_loader.py:34-98`).
4. The server scans external adapter folders and selects the highest numeric valid version (`SinAI-Training/work/serve_sinai.py:43-107`).
5. If discovery fails, its hard-coded grammar fallback is v13 (`:48-53`).

Conflicting documentation says v13 (`SinhalaJournalLLM/README.md:7-12`) or v22 (`manual dataset/README.md:14-18`; `README.md:32,109`). v25-v27 results exist, but adapter directories and runtime database settings are untracked. A live `/tasks` response or database settings snapshot is required.

The production feature is hybrid: model output plus chunking, correction diffing, lexicon suggestions, final-form rules, and substitution warnings. Suspicious substitutions are flagged, not reverted (`grammar_service.py:109-124`; `substitution_guard.py:233-286`).

The shipped gzip lexicon contains 74,561 word rows and metadata for 319,099 processed articles and 44,007,176 tokens. This conflicts with older comments describing approximately 78,537 words and 215,000 articles (`sinhala_lexicon.txt.gz`; `lexicon.py:34-64`).

---

# 4. Summarization component

## Objective and datasets

The current objective is abstractive Sinhala news summarization with short, medium, and long length control (`SinAI-Training/summarizer/abstractive/6_train_summarizer.py:1-20`).

| Dataset | Verified size/status | Purpose |
|---|---|---|
| `/home/jovyan/summarizer/all_articles_merged.json` | File absent; count **NOT FOUND** | Source articles for teacher generation |
| `/home/jovyan/summarizer/data/6_multilength_summaries.jsonl` | 35,569 documented; file absent | v06 multi-length silver corpus |
| `/home/jovyan/summarizer/data/6_multilength_summaries_clean.jsonl` | 35,547 implied after 22 removals; file absent | v07 cleaned corpus |
| `/home/jovyan/summarizer/data/5_qwen_summaries.jsonl` | Historical script says 151,438 raw records; file absent | v05 and optional long supplement |
| `SinAI-Training/summarizer/6_eval_results/v06_eval_20260726_025630.json` | 45 generations | Only tracked authoritative generative result |

The multi-length schema includes article fields, `teacher_model`, `summary_short`, `summary_medium`, `summary_long`, and rejection reasons (`6_multilength_summary_generator.py:291-327`).

Preprocessing applies NFC normalization, HTML/URL removal, whitespace collapse, URL deduplication, Sinhala-ratio checks, and content/title length filters (`summarizer/1_preprocess.py:22-84,114-152`).

## Teacher generation

| Teacher/method | Status |
|---|---|
| Llama-4 Maverick through NVIDIA NIM | Implemented for v02 |
| DiffusionGemma 26B | Implemented for v03/v04 |
| Gemini 2.0 Flash | Implemented (`5_gemini_summary_generator.py:41-52,192-245`) |
| Qwen3 Next 80B | Implemented for v05 (`5_qwen_summary_generator.py:36`) |
| ChatGPT browser generation | Historical implementation at commit `2116e10`; final-data use unproven |
| v06 nine-router gateway | Implemented, but default model is alias `summarizer`; actual model **NOT FOUND** |

Whether Gemini or ChatGPT generated final v06 targets is **NOT FOUND**. The final 35,569-record teacher provenance is not reproducible from repository contents. Some teacher scripts contain committed credentials; their values are intentionally omitted.

The v06/v07 trainer expands articles into length-specific samples before its 85/15 split, so different lengths from the same article can cross partitions (`6_train_summarizer.py:216-234,286-289`).

## Summarization experiment chronology

| Version | Model/data | Configuration | Result/status |
|---|---|---|---|
| Early mT5 | `google/mt5-base`; article-to-title pseudo-summary | 512/64; 90/5/5; 5 ep.; batch8; LR5e-5 | **NOT FOUND** |
| Alternate mT5 | `google/mt5-base` | 5 ep.; batch2×16; LR5e-5; checkpointing | **NOT FOUND** |
| mT5-LoRA v01 | mT5-base + Qwen summaries | input512/target150; r32/α64; 5 ep.; batch4×8; LR3e-4 | **NOT FOUND** |
| SinLLaMA v01 | `summarization_dataset.jsonl` | seq1024; r16/α32/drop.05; 5 ep.; batch2×8; LR2e-4 | **NOT FOUND** |
| v02 | Original/Gemini/Llama-4 alternatives | seq2048; r32/α64/drop0; 5 ep.; batch2×8; LR2e-4 | Exact completed recipe/result **NOT FOUND** |
| v03 | DiffusionGemma | Same with dropout0 | Later source documents an Unsloth 4-bit CUDA dtype failure |
| v04 | DiffusionGemma | Dropout corrected to .05 | Result **NOT FOUND** |
| v05 | Qwen3 Next 80B | seq2048; r32/α64/drop.05; 5 ep.; batch2×8; LR2e-4 | Result **NOT FOUND** |
| v06 | Multi-length + optional Qwen long | seq2048; r32/α64/drop.05; 3 ep.; batch2×8; LR2e-4; 4-bit BF16; completion-only | Tracked evaluation result |
| v07 | Cleaned v06 | Same plus word-glue/numeric-unit checks | Trainer exists; run/log/adapter/result **NOT FOUND** |

Extractive TF-IDF, TextRank, RAKE, YAKE, and KeyBERT code exists under `SinAI-Training/summarizer/extractive/`. `summarizer/compare_results.py:1-12,138-183` was intended to compare extractive and mT5 outputs, but required result files are absent. ByT5 is **NOT FOUND**.

## v06 authoritative result

| Length | N | ROUGE-1* | ROUGE-2* | ROUGE-L | Mean compression | In-band | Clean ending |
|---|---:|---:|---:|---:|---:|---:|---:|
| Short | 15 | .7746 | .5857 | .6163 | .1177 | 93.33% | 100% |
| Medium | 15 | .8046 | .5729 | .5789 | .2313 | 100% | 100% |
| Long | 15 | .8439 | .5982 | .5489 | .3629 | 100% | 100% |

Source: `SinAI-Training/summarizer/6_eval_results/v06_eval_20260726_025630.json:1-20`.

ROUGE-1/2 were reconstructed from stored examples; the scorer tokenizes Sinhala into grapheme clusters, limiting comparison to conventional word-level ROUGE (`6_test_summarizer.py:95-148`). BERTScore, semantic factuality metrics, human evaluation, significance, and authoritative latency are **NOT FOUND**.

## Summarization failures and limitations

- A stored long prediction changes Portugal-Uruguay to Pakistan (`v06_eval_20260726_025630.json:49-55`).
- Cleaning notes report 21 genuine word-glue/numeric-unit defects and one false positive, including 100-1000× scale errors (`clean_multilength_dataset.py:15-21`).
- The raw digit checker does not catch every entity or scale-word substitution (`6_multilength_summary_generator.py:147-152`).
- Older `no_repeat_ngram_size=3` evaluation could corrupt opening Sinhala graphemes (`6_test_summarizer.py:6-20`).
- The evaluator samples fifteen articles from the same full silver file rather than a persisted blind partition (`:214-241`).
- All saved evaluation URLs are Ada Derana domains.
- Cross-length article leakage is possible.

**Best supported summarizer:** v06.  
**Latest implemented recipe:** v07, not proven trained/evaluated.  
**Exact deployed adapter:** **NOT FOUND**; README claims v06, server fallback is v04, and runtime discovery can override both.

---

# 5. Style rewriting component

## Styles, labels, and data

The five implemented styles are formal news, editorial/opinion, sports, youth/conversational, and feature/narrative (`generate_style_dataset.py:60-155`). Production accepts `formal`, `sports`, `youth`, `editorial`, and `feature` (`SinAI-Training/work/tasks/style.py:6-86`).

| Dataset | Evidence/status |
|---|---|
| `/home/jovyan/style_rewriter/data/style_dataset2_final_cleaned.jsonl` | Trainer documents 7,555 rows; file absent (`train_style.py:22-28,397-399`) |
| `style_dataset2_dub.jsonl` | Comments conflict between ~10,866 and ~22,237 rows/articles; file absent |
| Planned expanded set | 14,320 = 2,864 articles ×5; generator says 6,765 rows still needed (`generate_style_dataset.py:4-15`) |

Schema: `content`, `category`, `url`, `date_published`, `style`, `rewritten_text`, with optional status/error/QC fields (`train_style.py:182-222`).

Labels are synthetic. The generator uses DeepSeek V4 Pro through NVIDIA NIM, temperature .15, top-p .85 (`generate_style_dataset.py:4-10,35-36,162-178`). Human-authored rewrite targets are **NOT FOUND**.

Only formal 2,471 and feature 539 are documented; other style counts are **NOT FOUND** (`train_style.py:358-363`).

`validate_rewrite()` detects length, truncation, and repetition issues, but `process_one()` does not consistently persist these QC issues (`generate_style_dataset.py:233-266,297-316`). A correction pass writes `corrected_text`, while the trainer reads `rewritten_text`; use of corrected targets is **NOT FOUND** (`Correct_style_dataset.py:120-165,340-413`; `train_style.py:200-216`).

The current trainer splits by URL 85/15 and upsamples minority styles only in training (`train_style.py:355-389,462-485`). Missing URLs fall back to process-specific object IDs and are not reliably grouped.

## Style experiment chronology

| Version | Dataset/configuration | Result |
|---|---|---|
| v01 | **NOT FOUND** | **NOT FOUND** |
| v02 | Application README reference only | Training/evaluation **NOT FOUND** |
| v03-v06 | **NOT FOUND** | **NOT FOUND** |
| v07 | `style_dataset.jsonl`; seq4096; r32/α64/drop.05; 8 ep.; batch2×8; LR2e-4 | Saved result **NOT FOUND** |
| v08 | ~10,866 documented; r32/α64; 5 ep.; LR2e-4 | Comments claim train .4764, eval 1.087, 2.28× gap; raw log **NOT FOUND** |
| v09 | Expanded data; r16/α32; 3 ep.; LR2e-4; WD.01 | Comments claim eval .849 and 1.26× gap; raw result **NOT FOUND** |
| v10 | r24/α48; 3 ep.; LR2e-4; stronger factual/gender/quote constraints | Result **NOT FOUND** |
| v11 | Cleaned 7,555; seq4096; r24/α48/drop.05; 5 ep.; batch2×8; LR1e-4; WD.01; warmup100; 4-bit BF16 | Adapter/log/evaluation **NOT FOUND** |

The v11 script still displays “Training v05” while writing v11 (`train_style.py:397-399`).

## Style evaluation and failures

`test_style.py:231-471` implements word ROUGE-1/2, simplified BLEU, TF-IDF cosine, length preservation, diversity, heuristic style markers, and a weighted custom quality score. That score is later called “accuracy” even though it is not classification accuracy (`:797-817`). The evaluator selects up to the twenty longest held-out articles with all five styles (`:605-688`), and its expected result JSON is absent.

`test_style_long.py` is explicitly a prototype. Its static ROUGE/BLEU/cosine/custom-score values have no adapter, dataset, timestamp, or machine-readable provenance and are not authoritative (`:1-7,183-215`).

Direct qualitative problems include:

- invention of people, innings, sixes, fuel details, and consumer effects (`test_style_long.py:71-180`);
- female-to-male honorific changes, altered quotes, English insertion, and fabricated duration (`train_style.py:159-171`);
- Sinhala morphology/character corruption caused by repetition constraints (`test_style.py:43-84,493-520`).

Human evaluation, trained style-classifier accuracy, BERTScore/entailment, entity/number consistency, latency, and significance testing are **NOT FOUND**.

### Critical train/serve prompt mismatch

The trainer requires an English prompt containing `STYLE_RULES`, `### IMPORTANT RULES`, and `### Input:` and says inference must be byte-identical (`train_style.py:97-176`). The live server instead uses a substantially different Sinhala instruction and `Text:` field (`SinAI-Training/work/tasks/style.py:6-98`). Current serving is therefore prompt-out-of-distribution relative to the trainer/evaluator.

**Best verified style model:** **NOT FOUND**.  
**Latest recipe:** v11, not proven completed.  
**Exact deployed adapter:** **NOT FOUND**; documentation/fallback mention v07, while an older application README says v02.

---

# 6. Headline generation component

## Objective and data

The objective is concise Sinhala newsroom headline generation preserving the principal actor, event, number, or outcome (`train_headline.py:62-80`). v18+ implements short 3-5, medium 6-7, and long 8-10 word bands (`train_headline_v18.py:1-21,62-81`).

Referenced files `headline_dataset_48k_balanced_{train,val}.jsonl` are absent (`train_headline.py:10-13`). Scripts describe approximately 48K examples across twelve categories, but exact train/validation counts cannot be verified (`:40-44,181-187`).

Schema:

```text
input:  Category: <category>\nArticle: <body>
output: <headline>
```

Evidence: `train_headline.py:91-109`.

v17 performs NFC and language/length filtering and truncates articles to 2,000 characters (`:47-69,91-125`). v18 constrains labels to 3-10 words and balances bands by downsampling (`train_headline_v18.py:62-103,136-205`). v19 cleans output-label media artifacts; v20 cleans expanded artifacts in input and output (`clean_headline_dataset.py`; `clean_headline_dataset_v20.py`).

Hiru/ITN media tags occur in cleaning rules, but a reproducible construction link from raw news corpora to the 48K set is **NOT FOUND**. NSINA usage is **NOT FOUND**.

## Headline experiment chronology

v17-v20 generally use the pre-merged SinLLaMA base, 4-bit BF16, sequence 768, r64/α128/dropout .08, 8 epochs, batch2×accum4, LR5e-5, WD.05, warmup .08, completion-only loss, and early stopping (`train_headline.py:10-33,195-269`; `train_headline_v18.py:33-56,272-378`).

| Version | Change | Result/status |
|---|---|---|
| v01-v12 | **NOT FOUND** | **NOT FOUND** |
| v13 | Deployment-history reference | Trainer/result **NOT FOUND** |
| v15 | 24K imbalanced baseline | Embedded R1 .1389, R2 .0247, RL .1353, BLEU .0020; raw artifact absent |
| v17/v16 ambiguity | 48K balanced; fixed 4-7-word prompt | Output path says v17, banners/metadata say v16 |
| v18 | Length conditioning and band balancing | Documented 900-generation evaluation |
| v19 | Cleaned target labels | Best documented trade-off; raw JSON absent |
| v20 | Cleaned input and output tags | Tested; no clear improvement; not retained over v19 |

## Documented results

The following appear in `SinAI-Training/CLAUDE.md`, not raw result JSON.

| Version | N | Short | Medium | Long | Overall | ROUGE |
|---|---:|---:|---:|---:|---:|---|
| v18 | 300 articles ×3 | 88.7% in-band; .3% artifact | 76.0%; 11.0% | 78.0%; 22.3% | 80.9% in-band; 11.2% artifact | R1 .124; RL .121 |
| v19 | 300×3 | 89.7%; 0% | 74.3%; .3% | 75.0%; 3.0% | 79.7%; 1.1% | R1 .134; RL .130 |
| v20 | 300×3 | 84.7%; .3% | 75.3%; 1.0% | 79.7%; 2.3% | 79.9%; 1.2% | Summary ROUGE **NOT FOUND** |

Evidence: `SinAI-Training/CLAUDE.md:166-212,259-289`. The repository retains v19 because artifacts fell roughly tenfold relative to v18 while band adherence remained similar. v20 did not improve artifacts and regressed short outputs.

## Headline evaluation weaknesses

The evaluator uses seed 42, 300 validation articles, three requested bands, temperature .3, top-p .9, repetition penalty 1.1, and no-repeat bigram 2 (`test_headline_v18.py:28-37,123-148,189-310`).

Limitations:

1. Training includes `Category:` and `Article:` labels, but evaluation strips them and passes only article text (`train_headline_v18.py:110-133`; `test_headline_v18.py:191-208,227-247`). Production includes those labels (`SinhalaJournalLLM/apps/backend-api/app/core/prompts.py:142-182`). Metrics are not measured under the train/production prompt.
2. One artifact token is misspelled differently in the detector and cleaner, potentially undercounting it (`test_headline_v18.py:53-57`; `clean_headline_dataset.py:37`).
3. v18-v20 use progressively cleaned validation files rather than a fixed blind test.
4. v20 tests already-cleaned inputs and cannot evaluate copying from dirty inputs (`CLAUDE.md:269-285`).
5. Human/factual/entity evaluation, latency, repeated seeds, confidence intervals, and external testing are **NOT FOUND**.

Backend stripping, retrying, trimming, and deduplication mean user-visible performance is model-plus-rules (`headline_service.py:1-24,43-91,107-201`).

## Image integration

| Stage | Current checked-out implementation |
|---|---|
| Visual prompt | Groq, default `llama-3.3-70b-versatile` (`visual_prompt_service.py:1-11,41-68`) |
| Image generation | OpenAI Images API, default `gpt-image-2` (`image_generation_service.py:1-25,62-155`) |
| Output | 1536×1024, high quality, up to three attempts |
| Access | Admin-only (`api/v1/image_generation.py:21-31`) |
| Storage | Optional Cloudinary and headline history (`cloudinary_service.py:1-66`) |

The headline route still catches/documents OpenRouter while the current service raises Groq errors, creating an exception-handling conflict (`api/v1/headline.py:30,71-95`; `visual_prompt_service.py:11,41-68`).

Historical attempted providers include Gemini, Nano Banana, Pixazo, Cloudflare Workers AI, OpenRouter Krea, Hugging Face SDXL, Pollinations, and OpenAI. Commit `69dccf3` implemented Nano Banana but was later replaced; it is not current deployment.

**Best documented headline model:** v19.  
**Latest experiment:** v20.  
**Exact deployed model:** **NOT FOUND**; repository claims conflict among v17, v18, and v19, while the server fallback/web default are v17.

---

# 7. Cross-component model strategy

The core strategy is one shared foundation model with separate task adapters. The overall application is hybrid because it includes hosted fallbacks, rules, extractive methods, and separate visual/image services.

| Task | Foundation | Latest/best evidence | Server fallback | Verified deployment |
|---|---|---|---|---|
| Grammar | `SinLLaMA-merged-base` | v27 best aggregate; v25 best unseen; v26 best stage4 | v13 | **NOT FOUND** |
| Summarization | Same | v06 best verified; v07 code only | v04 | **NOT FOUND** |
| Style | Same | v11 latest recipe; best result **NOT FOUND** | v07 | **NOT FOUND** |
| Headline | Same | v19 preferred; v20 latest experiment | v17 | **NOT FOUND** |

Runtime database settings can override adapters, and blank settings select the server's discovered highest version (`settings_registry.py:90-98,138-186`; `model_gateway.py:212-248`).

---

# 8. Training infrastructure

## Verified grammar environment

| Item | Value |
|---|---|
| GPU | 1× NVIDIA A40 |
| Reported maximum GPU memory | 44.352 GB |
| OS | Linux |
| PyTorch | 2.6.0+cu124 |
| CUDA Toolkit | 12.4 |
| Compute capability | 8.6 |
| Triton | 3.2.0 |
| Transformers | 5.5.0 |
| Unsloth | 2026.4.6 |
| Precision | BF16 supported/used |
| Quantization | 4-bit base |
| v24-v26 trainable parameters | 83,886,080 / 8,204,914,688 |
| v27 trainable parameters | 10,485,760 / 8,131,514,368 |

Evidence: `manual dataset/Tested_results/train log v24.md:39-63`; `v25 adapter training logs.md:39-63`; `v26 traing log.md:38-62`; `v27 trainlog.md:38-62`.

| Run | Duration |
|---|---:|
| v24 | ~23,640 seconds / 6.57 h |
| v25 | ~30,660 seconds / 8.52 h |
| v26 | ~22,820 seconds / 6.34 h |
| v27 | ~22,890 seconds / 6.36 h |

Exact PEFT, bitsandbytes, Python, CPU, and system RAM versions for these runs are **NOT FOUND**.

Exact hardware for summarization, style, and headline is **NOT FOUND**; the grammar A40 cannot automatically be generalized. Current inference requests NF4, double quantization, BF16 compute, and `device_map="auto"` (`serve_sinai.py:117-132`). The backend uses Python 3.12; the web build uses Node 20 (`SinhalaJournalLLM/apps/backend-api/Dockerfile`; `apps/web-app/Dockerfile`).

Current GPU host/vendor, production CUDA environment, CPU/RAM, topology, energy usage, and authoritative latency are **NOT FOUND**.

---

# 9. Model-training methodology

| Method | Actually implemented? | Qualification/evidence |
|---|---|---|
| Transfer learning | Yes | Upstream SinLLaMA adapter/tokenizer merged into Llama-3-8B |
| Continual pretraining by this project | **NOT FOUND** | The project consumes upstream SinLLaMA rather than reproducing CPT |
| Supervised fine-tuning | Yes | All task trainers |
| Instruction fine-tuning | Yes | Alpaca/chat instruction-input-response formats |
| LoRA/PEFT | Yes | Separate task adapters |
| 4-bit QLoRA | Yes | Unsloth/4-bit trainers |
| Completion-only loss | Yes | Grammar v16+ and current generative trainers |
| Synthetic data | Yes | Grammar corruption and style rewrites |
| Teacher-model generation | Yes | Summary/style generator scripts |
| Prompt engineering | Yes | Length bands, preservation/style rules |
| Curriculum learning | **NOT FOUND** | Versioned data expansion is not within-run curriculum |
| Automated hyperparameter optimization | **NOT FOUND** | Changes are manually selected |
| Multiple-seed selection | **NOT FOUND** |
| Hybrid model/rule system | Yes | Lexicon, guards, chunking, trimming, fallbacks |

The implemented methodology is iterative supervised PEFT/QLoRA over handcrafted, corpus-corrupted, and teacher-generated data. Repeated decisions on the same grammar benchmark create adaptive test-overfitting risk.

---

# 10. Evaluation methodology

| Component | Test design | Metrics | Main limitations |
|---|---|---|---|
| Grammar | Four stages; 154 total | Exact, change-needed, preservation, over-correction, grapheme ROUGE, GLEU, Char-F1, token overlap | Pair contamination, evolving gold, repeated use, small tests, no external baseline |
| Summary | 15 articles ×3 lengths | Grapheme ROUGE, compression, band adherence, clean ending | Possible leakage, tiny/source-limited sample, no factuality/human metric |
| Style | Up to 20 held-out articles ×5 | ROUGE, BLEU, TF-IDF cosine, length, markers, custom score | Result absent, longest-item selection, heuristic “accuracy,” serving mismatch |
| Headline | 300 validation articles ×3 | In-band, artifact, own-band ROUGE/BLEU | Prompt mismatch, changing validation files, stochastic single runs, no blind/human test |

Important methodological limitations:

1. Grammar validation is a random 5% row split, allowing oversampled duplicates across train/eval (`train_grammar.py:328-345`).
2. The grammar contamination audit found 1,030 stage2, 934 stage3, 1,135 stage4, and 67 stage5 rows teaching benchmark correction pairs (`train_roadmap.md:316-341`).
3. Exact row non-overlap does not remove correction-pair or shingle contamination.
4. Grammar gold changed after early runs (`patch_gold_v10.py`).
5. Summary splitting after length expansion permits same-article cross-partition leakage.
6. Summary evaluation samples the full teacher file, not a persisted blind split.
7. Style's URL split is stronger in design, but no result proves it ran.
8. Headline evaluation omits part of its training/production prompt.
9. No uniform baseline comparison exists across all tasks.
10. Confidence intervals, power analysis, and multi-seed significance are mostly **NOT FOUND**; grammar's Fisher test is the exception.

---

# 11. User evaluation and SINAI feedback

## Implemented instrumentation

- Persistent anonymous device/session IDs (`SinhalaJournalLLM/apps/web-app/src/lib/research.js:1-24,60-92`).
- `shown`, `accepted`, and `rejected` suggestion telemetry (`useSuggestionTelemetry.js:1-13,39-127`).
- Event API/repository (`api/v1/events.py:1-89`; `events_repository.py:1-60`).
- Telemetry and `suggestion_events` schema (`schema.sql:465-530`).
- Google Form link in web sidebar (`Sidebar.jsx:49-105`).

A device ID is explicitly not a person and may split one participant or merge multiple shared-device users (`app/core/research.py:20-25`; `schema.sql:478-480`). Accept/reject is behavior, not independently verified linguistic correctness.

| Evaluation item | Status |
|---|---|
| University journalism-student distribution through WhatsApp | Planned/documented |
| Google Form contents | **NOT FOUND** |
| Google Form responses/results | **NOT FOUND** |
| SUS questionnaire | **NOT FOUND** |
| Likert questions | **NOT FOUND** |
| Participant count/roles | **NOT FOUND** |
| Completed journalist testing | **NOT FOUND** |
| Completed student usability study | **NOT FOUND** |
| Consent/ethics material | **NOT FOUND** |
| Inter-rater agreement | **NOT FOUND** |

---

# 12. SINAI application

## Web application

Implemented:

- dashboard, four task pages, Optimize, protected history/settings/profile/plans, onboarding, and admin console (`App.jsx:453-486,536-580`);
- five styles, three summary lengths, three headline bands, counts, and headline model options (`toolOptions.js:9-52`);
- Optimize orchestration rather than a fifth model (`toolMeta.js:37-50`);
- editable visual prompts and admin-only image generation (`HeadlineOutputPanel.jsx:48-240,346-354`);
- external feedback form (`Sidebar.jsx:49-105`);
- backend tokens in `localStorage`, with an XSS-risk comment (`authClient.js:1-17,30-129`).

Limitations: only headline exposes a normal-user adapter picker; image generation is admin-only; exact deployed frontend revision is **NOT FOUND**. Anonymous persistence is inconsistent—grammar is actor-aware, while headline/style/summary generally pass only `user_id`.

## Chrome extension

Implemented:

- Manifest V3 v1.1.0 (`manifest.json:1-18`);
- grammar/headline/style/summary context menus (`background.js:74-127`);
- email/password and Google OAuth with token refresh (`background.js:147-276,367-430`);
- four tools plus Optimize (`popup.html:45-150,153-301`);
- local and server history (`background.js:279-311,694-750`; `popup.js:1237-1315`);
- selection extraction/replacement for form fields and contenteditable (`content.js:649-763,920-1052,1230-1407`).

Limitations: no visual/image workflow, feedback link, adapter picker, or headline-length picker. Chrome Web Store publication is **NOT FOUND**. The README's “Load unpacked” procedure supports development installation only.

## Google Docs add-on

Implemented:

- Apps Script V8 manifest (`appsscript.json:1-28`);
- sidebar/menu, selection extraction, replacement, insertion (`Code.js:8-175`);
- four tools and Optimize (`Sidebar.html:36-142,148-250`);
- email/password signup/login/reset and refresh (`Code.js:194-397`);
- server history/statistics (`Code.js:399-407`).

Limitations: Google sign-in is unavailable (`Code.js:202-208`); `UrlFetchApp` buffers Optimize rather than incrementally reading NDJSON (`:409-443`); backend URL is effectively hard-coded (`:177-191`); no visual/image, feedback, or adapter picker exists. `.clasp.json` proves Apps Script linkage but Marketplace publication is **NOT FOUND**.

---

# 13. Deployment

| Item | Repository-supported finding |
|---|---|
| Frontend hosting | Umbrella README claims Render at `sinai.onrender.com` (`README.md:6,91-101`) |
| Backend API | Web, Chrome, and Docs default to `https://sinhalajournalllm.onrender.com/api/v1` |
| Newer domains | Portfolio claims `sin-ai.app` and workspace `chat.sin-ai.app` |
| Deployment service | Newer docs say Render; older product/infra docs say Coolify |
| Database technology | Supabase/PostgreSQL/PostgREST |
| Database hosting | Tracked environment points to hosted Supabase; old docs say self-hosted; current truth **NOT FOUND** |
| GPU inference host/vendor | **NOT FOUND** |
| Model storage | External `/home/jovyan/.../models/adapters` |
| Chrome Web Store status | **NOT FOUND** |
| Google Marketplace status | **NOT FOUND** |
| Vercel deployment | **NOT FOUND** |
| `render.yaml` or equivalent | **NOT FOUND** |
| Live DNS/service-state artifact | **NOT FOUND** |

`SinhalaJournalLLM/infra/docker-compose.yml:1-14` is development-only. A tracked backend `.env` contains live-looking secrets; values are omitted. Their presence is a security/reproducibility concern, not proof of production configuration.

---

# 14. Research contributions supported by evidence

## Scientific contributions

Potential contributions, without unverified novelty claims:

1. Versioned Sinhala grammar datasets and staged tests combining handcrafted categories, clean controls, corpus corruption, and real-news examples.
2. Empirical evidence that exact correction-pair exposure strongly predicts grammar success, including a Fisher p=.0014 result in the older audit (`train_roadmap.md:25-58`).
3. Evidence that target quality may matter more than raw data volume: v23's 9,000 extra rows did not improve generalization, while v10 target repair recovered v25/v26.
4. A controlled low-rank grammar experiment: v27 r4 improved aggregate/stage5 slightly but did not improve unseen-pair transfer (`train_grammar_v27.py:245-310`).
5. Length-conditioned Sinhala abstractive summarization with a tracked v06 15×3 evaluation and teacher-data quality audit.
6. Headline length-conditioning and artifact-cleaning experiments; v19 sharply reduced documented artifacts.
7. Negative evidence on Sinhala decoding constraints, including grapheme/morphology damage from no-repeat and repetition settings.

## Engineering contributions

1. Shared-base multi-adapter SinLLaMA GPU server.
2. SinLLaMA/OpenRouter/mock resilient inference gateway.
3. SINAI web platform with auth, history, admin, telemetry, and Optimize.
4. Chrome extension and Google Docs integration.
5. Grammar safeguards: chunking, lexicon, sentence-final checks, entity/substitution warnings.
6. Headline visual-prompt and image workflow using Groq, OpenAI Images, and optional Cloudinary.

---

# 15. Negative results and important findings

| Hypothesis/problem | Experiment | Result | Decision/interpretation |
|---|---|---|---|
| More grammar data improves v13 | v14 | Identical score | Investigate full-sequence loss |
| Old TRL collator enables completion-only | v15 | Two failed attempts | Rewrite trainer API |
| Larger LoRA/data improves grammar | v18 | Large gain | Positive but two variables changed |
| High stage2/3 indicates generalization | v19 stage4 | 93/90% falls to 58.3% | Build harder corpus data |
| More targeted data solves stage5 | v23 | Aggregate/stage5 worsen | Volume alone insufficient |
| Shorter schedule fixes v23 | v24 | 57.8% current-gold | Diagnose targets |
| Target repair matters | v25/v26 | 66.2/65.6%, unseen 50/47% | Data quality materially matters |
| Four epochs best use v10 | v25 | Eval loss rises after epoch 3 | Stop at three epochs |
| Lower rank forces rule learning | v27 r4 | Untaught 48%, below v25 | Primary hypothesis unsupported |
| Names act like ordinary spelling errors | v23-v27 | Entity substitution persists | Add preservation data/warnings |
| Dropout0 works in 4-bit summary LoRA | v03 | Unsloth CUDA dtype problem | Restore .05 dropout |
| Standard no-repeat constraints help Sinhala | Early summary/style | Grapheme/morphology corruption | Remove/relax constraint |
| Teacher summaries are reliable | v06 corpus | Numeric-unit/glue defects | Add v07 cleaning |
| ROUGE captures factuality | v06 result | High overlap with Portugal->Pakistan error | Factuality metrics required |
| v08 style generalizes | v08 | Commented 2.28× train/eval gap | Lower rank/epochs, add WD |
| v09 fixes style quality | v09 | Gender, quote, morphology, numeric errors persist | Stronger constraints/cleaning |
| Style train and serving prompts match | Current integration | They substantially differ | Production evaluation is unrepresentative |
| Length conditioning alone cleans headlines | v18 | 11.2% artifacts | Clean labels in v19 |
| Cleaning headline inputs improves v19 | v20 | No artifact gain; short regression | Retain v19 |
| v20 tests dirty-input copying | Cleaned v20 validation | Cannot test hypothesis | Needs fixed dirty blind set |

---

# 16. Consolidated research-results table

| Component | Baseline | Best supported model | Dataset size | Primary metric | Best result | Main limitation | Deployment |
|---|---|---|---:|---|---|---|---|
| Grammar | v13: 49.1% stage2 exact | v27 aggregate; v25 unseen; v26 stage4 | 36,006 | Exact match | v27 66.9% aggregate, 43.1% stage5, 97.4% preservation; v25 50% unseen | Pair dependence, contamination, copying, names | Integrated; exact adapter **NOT FOUND** |
| Summarization | Extractive/mT5 result **NOT FOUND** | v06 | 35,569 documented | Grapheme ROUGE-L and adherence | .6163 short/.5789 medium/.5489 long; N=15 each | Possible leakage, tiny source-limited sample, factual errors | Integrated; exact adapter **NOT FOUND** |
| Style | Authoritative baseline **NOT FOUND** | **NOT FOUND**; v11 latest recipe | 7,555 documented | Authoritative completed metric **NOT FOUND** | Prototype only; not final evidence | Missing artifact, synthetic labels, factual errors, prompt mismatch | Integrated; exact adapter **NOT FOUND** |
| Headline | v15 embedded comparison | v19 | “48K”; exact split **NOT FOUND** | Artifact and band adherence | 1.1% artifact, 79.7% in-band, R1 .134/RL .130 | Raw results absent, prompt mismatch, no blind/human/factual test | Integrated; exact adapter **NOT FOUND** |

---

# 17. Research-paper readiness

## READY FOR PAPER

- Official project identity, ID, component scope, and shared-base/multi-adapter design.
- Current source-level architecture and task data flows.
- Grammar dataset lineage, counts, categories, corruption rules, and staged tests.
- Grammar v13-v27 experiment chronology.
- Current-gold v24-v27 results and detailed v27 metrics.
- Grammar memorization, target-quality, schedule, and rank negative findings.
- v06 summarization configuration and tracked result JSON.
- v06/v07 teacher-data quality findings.
- Headline v18-v20 documented comparison with explicit caveats.
- Implemented web, Chrome, Docs, authentication, telemetry, and image workflow.

## NEEDS VERIFICATION

- Exact adapters installed on the production GPU server.
- Runtime database adapter overrides.
- Current live hosting/domain mappings.
- Hosted versus self-hosted production Supabase.
- Exact teacher behind final v06 summaries.
- Exact headline 48K construction, counts, provenance, and split.
- Whether corrected style outputs entered final training.
- Whether v11 style was actually trained.
- Raw v18-v20 headline result files.
- v08/v09 style losses retained only in comments.
- Chrome/Docs publication status.
- Whether uncommitted grammar curation will define a future dataset/version.

## STILL MISSING

- Formal research questions and pre-registered hypotheses.
- Comparable baselines on identical held-out tests.
- Tracked generative datasets and immutable split manifests.
- Independent blind tests.
- Journalist/human evaluation results.
- SUS/Likert instruments, participant counts, consent, and ethics evidence.
- Inter-rater agreement.
- Statistical significance, confidence intervals, and repeated seeds.
- Standard GEC edit precision/recall/F0.5.
- BERTScore and stronger semantic/factual metrics.
- Entity/number consistency tests.
- Production latency, throughput, and resource benchmarks.
- Full hardware/software lockfiles for generative experiments.
- CPU/RAM/energy reporting.
- Adapter weights, checksums, model cards, and upstream revision hashes.
- Dataset/teacher-output licensing analysis.
- Reproducible deployment manifests and live runtime snapshots.

---

# 18. Research-oriented file index

Paths below are relative to the workspace root unless noted.

## Datasets

- `manual dataset/cleaned_v10_full.jsonl` — v25-v27 grammar training set.
- `manual dataset/cleaned_v9_full.jsonl` — v23/v24 set before target repair.
- `manual dataset/cleaned_v8_full.jsonl` — v22 set.
- `manual dataset/stage5_round.jsonl` — 9,000 targeted synthetic rows.
- `manual dataset/itn_merged.json` — 106,627-record ITN corpus used by grammar generation.
- `manual dataset/test data/grammar_test_stage2.jsonl` — 57-example test.
- `manual dataset/test data/grammar_test_stage3.jsonl` — 10-paragraph test.
- `manual dataset/test data/grammar_test_stage4.jsonl` — 36-example real-news test.
- `manual dataset/test data/grammar_test_stage5.jsonl` — 51-example hardest test.
- `manual dataset/New Dataset/count_articles.py` — inventories the raw news corpus.

## Dataset generation

- `manual dataset/scripts/build_corpus_dataset.py` — grammar corruption, filters, ambiguity and overlap guards.
- `manual dataset/scripts/build_stage5_round.py` — v9 targeted construction.
- `manual dataset/scripts/build_v10_round.py` — v10 target repair build.
- `manual dataset/scripts/patch_gold_v10.py` — test-gold revisions.
- `manual dataset/scripts/audit_v9_targets.py` — v9 answer-quality audit.
- `manual dataset/scripts/build_lexicon.py` — production spelling lexicon.
- `SinAI-Training/summarizer/abstractive/6_multilength_summary_generator.py` — v06 teacher schema/prompt/checks.
- `SinAI-Training/summarizer/abstractive/clean_multilength_dataset.py` — v07 quality cleanup.
- `SinAI-Training/work/sinllama/scripts/generate_style_dataset.py` — five-style DeepSeek generation.
- `SinAI-Training/work/sinllama/scripts/clean_headline_dataset.py` — v19 target cleanup.
- `SinAI-Training/work/sinllama/scripts/clean_headline_dataset_v20.py` — v20 input/output cleanup.

## Grammar training

- `SinAI-Training/work/sinllama/scripts/train_grammar.py` — current r32 recipe.
- `SinAI-Training/work/sinllama/scripts/train_grammar_v27.py` — controlled r4 experiment.
- `SinAI-Training/work/sinllama/download_model.py` — SinLLaMA acquisition.
- `SinAI-Training/work/sinllama/prepare_sinllama_base.py` — merged-base construction.

## Summarization training

- `SinAI-Training/summarizer/abstractive/6_train_summarizer.py` — authoritative v06 recipe.
- `SinAI-Training/summarizer/abstractive/7_train_summarizer.py` — v07 recipe; completed run unproven.
- `SinAI-Training/summarizer/abstractive/train_mt5_lora.py` — mT5-LoRA comparison.
- `SinAI-Training/summarizer/compare_results.py` — intended extractive/mT5 comparison.

## Style training

- `SinAI-Training/work/sinllama/scripts/train_style.py` — v11 recipe, prompt, split, and historical notes.
- `SinAI-Training/work/sinllama/scripts/Correct_style_dataset.py` — separate correction pass.

## Headline training

- `SinAI-Training/work/sinllama/scripts/train_headline.py` — fixed-length v17 trainer.
- `SinAI-Training/work/sinllama/scripts/train_headline_v18.py` — length-conditioned trainer.
- `SinAI-Training/work/sinllama/scripts/train_headline_v19.py` — cleaned-label trainer.
- `SinAI-Training/work/sinllama/scripts/train_headline_v20.py` — cleaned-input/output trainer.

## Evaluation and results

- `manual dataset/scripts/analyze_eval.py` — current-gold rescoring and pair exposure.
- `SinAI-Training/work/sinllama/scripts/test_grammar.py` — grammar metric definitions.
- `manual dataset/Tested_results/v27 results.md` — latest grammar result.
- `manual dataset/Tested_results/v27 trainlog.md` — latest grammar environment/loss.
- `manual dataset/Tested_results/v26 adap reults.md` — v26 result.
- `manual dataset/Tested_results/v25 adapter training logs.md` — v25 over-training evidence.
- `SinAI-Training/summarizer/abstractive/6_test_summarizer.py` — v06 evaluation.
- `SinAI-Training/summarizer/6_eval_results/v06_eval_20260726_025630.json` — tracked generative result.
- `SinAI-Training/work/sinllama/scripts/test_style.py` — style evaluation design; result absent.
- `SinAI-Training/work/sinllama/scripts/test_style_long.py` — non-authoritative prototype/failure examples.
- `SinAI-Training/work/sinllama/scripts/test_headline_v18.py` — headline evaluation and prompt mismatch.
- `SinAI-Training/work/sinllama/scripts/test_headline_v19.py` — v19 evaluator.
- `SinAI-Training/work/sinllama/scripts/test_headline_v20.py` — v20 evaluator.
- `SinAI-Training/CLAUDE.md` — retained headline v18-v20 result summaries.

## Backend and inference

- `SinAI-Training/work/serve_sinai.py` — adapter discovery, quantized loading, locking, routing.
- `SinAI-Training/work/tasks/style.py` — current style serving prompt.
- `SinAI-Training/work/tasks/summarizer.py` — summary prompt-version routing.
- `SinhalaJournalLLM/apps/backend-api/app/core/model_gateway.py` — fallback chain and overrides.
- `SinhalaJournalLLM/apps/backend-api/app/core/database.py` — actual PostgREST access.
- `SinhalaJournalLLM/apps/backend-api/app/core/auth.py` — current auth architecture.
- `SinhalaJournalLLM/apps/backend-api/app/services/grammar/grammar_service.py` — grammar production pipeline.
- `SinhalaJournalLLM/apps/backend-api/app/services/grammar/substitution_guard.py` — entity/substitution warnings.
- `SinhalaJournalLLM/apps/backend-api/app/services/headline/headline_service.py` — retries and band enforcement.
- `SinhalaJournalLLM/apps/backend-api/app/services/headline/visual_prompt_service.py` — Groq visual prompts.
- `SinhalaJournalLLM/apps/backend-api/app/services/image_generation_service.py` — OpenAI image generation.
- `SinhalaJournalLLM/apps/backend-api/schema.sql` — database/history/telemetry.
- `SinhalaJournalLLM/apps/backend-api/migrations/2026-08-02-self-hosted-auth.sql` — current auth migration.

## Frontend, Chrome extension, and Docs add-on

- `SinhalaJournalLLM/apps/web-app/src/App.jsx` — application routes/features.
- `SinhalaJournalLLM/apps/web-app/src/lib/toolOptions.js` — task and model options.
- `SinhalaJournalLLM/apps/web-app/src/lib/research.js` — anonymous research identity.
- `SinhalaJournalLLM/apps/chrome-extension/manifest.json` — extension version/permissions.
- `SinhalaJournalLLM/apps/chrome-extension/background.js` — auth, APIs, menus, and history.
- `SinhalaJournalLLM/apps/docs-addon/Code.js` — Docs integration/auth and buffering limits.
- `SinhalaJournalLLM/apps/docs-addon/Sidebar.html` — Docs feature surface.

## Documentation

- `R26-SE-037/README.md` — official name/ID and historical claims; not authoritative for current versions.
- `SinhalaJournalLLM/README.md` — application overview with stale auth/model/deployment sections.
- `manual dataset/README.md` — grammar design and historical production claims.
- `manual dataset/train_roadmap.md` — grammar rationale, contamination, and negative results.
- `manual dataset/stage5_manifest.md` — hardest-test construction.
- `manual dataset/downgrade_audit.md` — pending linguistic adjudication.
- `SinhalaJournalLLM/infra/README.md` — older Coolify/self-hosted deployment design.
- `R26-SE-037/Initial work/` — historical submitted implementation, not current SINAI architecture.

---

# Final factual snapshot

The latest README model tables are not authoritative. The latest repository evidence is:

- **Grammar:** v27 trained/evaluated; best aggregate exact match 66.9%. v25 retains the highest measured unseen-pair result at 50%.
- **Summarization:** v07 code/cleaning is latest, but v06 is the latest model with a tracked evaluation artifact.
- **Style:** v11 is the latest recipe, but no authoritative completed v11 result is present.
- **Headline:** v20 is the latest experiment; v19 is the repository's preferred documented model.
- **Production:** exact installed adapters remain **NOT FOUND** because the server scans an external adapter filesystem and runtime database overrides are unavailable.

Accordingly, the paper must distinguish **latest experiment**, **best experimentally supported model**, **application integration**, and **verified production deployment**. They are not interchangeable in the current repositories.
