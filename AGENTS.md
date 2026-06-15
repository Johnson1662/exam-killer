# Repository Guidelines

## Project Overview

Exam-Killer is a locally-run exam preparation tool for Chinese university students. Users upload past exam papers (PDF/images), which are parsed via **MinerU SDK** (OCR/markdown extraction), then annotated by an **LLM agent** into structured question banks and chapter-organized review guides. Backend is a **FastAPI + SQLite** monolith with SSE progress streaming. Frontend is a **vanilla JS single-page application** (hash-routed, no framework).

---

## Architecture & Data Flow

```
Upload PDF → MinerU OCR → raw/output.md + content_list.json + images/
  → LLM Agent (ReAct loop with read/write/edit tools) annotates questions using <!-- QUESTION: --> markers
  → sync_questions_from_annotated() parses annotations into SQLite
  → Two-phase review generation: outline → per-chapter guides
```

**Backend (Python/FastAPI):**
- `main.py` — FastAPI entrypoint, lifecycle hooks, route mounting, SPA static fallback, export/zip endpoints
- `config.py` — Path constants, file limits, allowed extensions, default LLM provider
- `db.py` — SQLite CRUD (~550 lines) with thread-local connections via `threading.local()` — synchronous, called from async routes (blocks event loop)
- `models.py` — Pydantic v2 request/response models
- `llm.py` — `LLMProvider` class wrapping `httpx.AsyncClient` (OpenAI-compatible). No streaming, no retry
- `sse.py` — Per-course SSE via `asyncio.Queue`, iterated by an async generator
- `sdk_extract.py` — Thin wrapper around `mineru.MinerU` (run inside `asyncio.to_thread`)
- `routes/` — 4 route modules: courses.py, files.py, questions.py, review.py
- `agent/` — ReAct agent loop (`core.py`) + prompts/ directory (extractor, classifier, review prompts)

**Frontend (Vanilla JS SPA):**
- `index.html` — Shell. Loads Google Fonts, KaTeX, marked.js, Lucide icons; 10 JS scripts in dependency order
- `css/style.css` — ~780 lines design system with CSS custom properties. No Bootstrap/Tailwind
- `js/api.js` — Thin `fetch` wrapper (`API.get/post/put/del/upload`)
- `js/config.js` — localStorage credential manager per LLM provider
- `js/router.js` — Minimal hash-based SPA router with param patterns
- `js/renderer.js` — KaTeX + marked.js pipeline with `[Qxxxx]` reference inlining
- Page modules: courses.js, course-detail.js, upload.js, question-bank.js, review-guide.js, settings.js

**Data flow:**
1. Upload PDF → file saved to `data/{course}/uploads/`
2. Parse (MinerU via background task) → `raw/{id}/output.md` + `content_list.json` + `images/` — SSE pushes progress
3. Extract (LLM Agent concurrently annotates each file's `output.md`) → `<!-- QUESTION: -->` markers written inline
4. Sync → regex-extracts annotated questions into SQLite `questions` table
5. Review generation (two-phase Agent: outline then per-chapter) → writes to `review-guide/{idx}-{title}.md`
6. Frontend serves via REST: filtered question browsing, rendered review guides with KaTeX + inline question embeds

---

## Key Directories

| Directory | Purpose |
|---|---|
| `backend/` | FastAPI app: routes, models, DB, LLM provider, SSE, Agent |
| `backend/agent/` | ReAct agent loop + LLM system prompts |
| `backend/agent/prompts/` | Extractor, classifier, review generation prompts |
| `backend/routes/` | API route modules (courses, files, questions, review) |
| `frontend/` | Vanilla JS SPA + CSS design system |
| `frontend/js/` | Page modules, router, API wrapper, renderer, config |
| `frontend/css/` | Single stylesheet with CSS custom properties |
| `data/{course_name}/` | Course data: uploads/, raw/{id}/, review-guide/, exports |
| `data/{course}/raw/{id}/` | MinerU output per file: output.md, content_list.json, images/ |
| `data/{course}/review-guide/` | Generated chapter study guides (Markdown) |
| `scripts/` | Ad-hoc cleanup & data-fix scripts |
| `project/` | Project documentation, specs, plans |

---

## Development Commands

```bash
# Run backend (dev)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Run backend (prod)
uvicorn backend.main:app --host 0.0.0.0 --port 8080

# Install dependencies
pip install -r requirements.txt

# Format Python (ruff)
ruff format backend/ scripts/

# Lint Python (ruff)
ruff check backend/ scripts/
```

No test runner, no CI, no pre-commit hooks configured. No Makefile.

---

## Code Conventions & Common Patterns

### Python (Backend)

- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes and Pydantic models
- **Type hints**: Used throughout (FastAPI) but not strict — many `Optional` handled loosely
- **Async pattern**: All route handlers are `async def`. SQLite calls are synchronous (block event loop — not run in executor). Background tasks via `asyncio.create_task` (no durability on crash)
- **Agent loop**: ReAct-style (`agent/core.py`). Provides 3 tools to LLM: `read` (file contents), `edit` (first-occurrence text replacement), `write` (create/overwrite). Path safety via `_resolve_path` escape check. 3 consecutive identical reads → abort. 300s timeout default. Runs tool calls inline, no parallelism
- **No DI container**: Routes register globally on `app`, modules import each other directly
- **No `.env` loading**: Config from module-level Python constants
- **SSE**: `asyncio.Queue` per course; cleaned up on stream end. Terminal signal: `done` or `[DONE]`. No TTL/reconnect
- **DB migrations**: None — schema created via `CREATE TABLE IF NOT EXISTS` at import. Additive columns manually added in `db.py` as "v0.2"
- **Error handling**: `try/except` in background tasks logging via SSE. No retry policies. No structured error propagation except SSE events

### JavaScript (Frontend)

- **Naming**: `camelCase` for identifiers, `UPPER_SNAKE_CASE` for constants, kebab-case CSS classes with BEM modifiers
- **Module pattern**: Script-tag modules (no ES module imports). Files communicate via global scope (`API`, `router`, `window.toast`, `getLLMConfig`, `renderMarkdown`)
- **Page pattern**: Each page handler is a function: fetch data → build HTML string → `innerHTML` into `#app` container → attach events → `lucide.createIcons()`
- **State**: No global store. Per-page state in local variables (re-fetched on mount). Config in localStorage. Module-level singletons (`_questionMap`, `_rgCourseId`) overwritten on each render
- **HTML generation**: Template literals. User input (course names, tag strings) interpolated raw into innerHTML — potential XSS vector
- **Event handling**: Mixed — `onclick` attributes and `addEventListener`. `stopPropagation` on overlapping click targets
- **CSS**: Self-contained custom properties, one breakpoint at 768px. No external UI framework

### Data Schema

SQLite tables (exam_killer.db):

- **courses**: id (PK), name (UNIQUE), dir_name (UNIQUE), created_at, chapters (TEXT JSON)
- **files**: id (PK), course_id (FK → courses ON DELETE CASCADE), filename (server), original_name, file_type, status (pending/extracting/parsed/annotated/failed), raw_dir, error_msg, created_at, chapters (TEXT)
- **questions**: id (PK), qid (UNIQUE, e.g. Q0001), course_id (FK), source_file_id (FK → files), qtype, content, options (TEXT JSON nullable), answer, explanation, knowledge_tags, difficulty (INT default 1), created_at, chapter_tags (TEXT)
- **knowledge_tags**: id (PK), course_id (FK), tag_name, UNIQUE(course_id, tag_name)

Status transitions: `pending → extracting → parsed → annotated` (or → `failed`).

Question dedup: by `qid` (e.g. Q0001). `sync_all_questions()` also dedups by first 120 chars of content.

---

## Important Files

| File | Role |
|---|---|
| `backend/main.py` | Application entrypoint, route mounting, lifecycle |
| `backend/db.py` | Schema creation, CRUD, annotation parsing |
| `backend/llm.py` | OpenAI-compatible LLM provider |
| `backend/agent/core.py` | ReAct agent loop with read/write/edit tools |
| `backend/agent/prompts/extractor.py` | Question annotation system prompt |
| `backend/agent/prompts/review.py` | Review guide generation prompts |
| `backend/routes/files.py` | Upload, parse (MinerU), extract (Agent) pipeline |
| `frontend/index.html` | SPA entry point, dependency load order |
| `frontend/js/api.js` | Fetch wrapper for all API calls |
| `frontend/js/renderer.js` | KaTeX + marked + `[Qxxxx]` inline question embed |
| `frontend/js/upload.js` | Upload/parse/extract UI with SSE progress |
| `frontend/js/question-bank.js` | Filtered question browsing |
| `frontend/js/review-guide.js` | Review guide generation + chapter viewer |
| `frontend/css/style.css` | Design system CSS |
| `DESIGN.md` | Design spec (palette, typography, components, layout) |
| `PRODUCT.md` | Product positioning and design principles |
| `requirements.txt` | Python dependencies |

---

## Runtime / Tooling Preferences

- **Python**: 3.12+ (runtime). Dependencies: `fastapi>=0.115`, `uvicorn[standard]>=0.34`, `mineru-open-sdk>=0.2.5`, `httpx>=0.27`, `python-multipart>=0.0.9`
- **Frontend**: No build step. Served as static files from FastAPI. CDN deps: KaTeX v0.16.9, marked.js v12, Lucide icons
- **LLM**: BYOK via OpenAI-compatible REST endpoint. Default: `https://opencode.ai/zen/v1` (model: `deepseek-v4-flash-free`). Configurable via Settings UI → localStorage
- **MinerU**: OCR SDK with its own token. Configurable via Settings UI → localStorage
- **Database**: SQLite (single file `exam_killer.db`). No connection pooling, no async driver. Thread-local connections
- **OS targets**: Windows 11 (primary dev), macOS/Linux compatible
- **No bundler, no transpiler, no containerization**. No test framework installed
- **Code formatter**: `ruff` (optional — not enforced in CI)

---

## Testing & QA

- **No test framework or test files exist** in the repository
- Testing is manual: run `uvicorn backend.main:app --reload`, open browser, exercise the UI
- **Verification checklist** (from `exam-killer-plan.md`):
  - Upload a PDF → watch SSE progress for MinerU parse
  - Click Extract → watch Agent annotation pipeline
  - Visit Question Bank → verify filter, tag chips, answer reveal
  - Generate Review Guide → verify chapter listing, rendered content, KaTeX math, `[Qxxxx]` links
- **Known issues** (from development history):
  - SQLite `threading.local()` connections are not async-safe — blocked on sync calls in async handlers
  - Agent `edit` tool uses first-occurrence string replace (not line-anchored) — can mangle content
  - Auto-reload (uvicorn `--reload`) can stall on large file writes
  - Data loss risk: re-uploading a file overwrites without confirmation
  - Formula rendering: LaTeX negation pattern `\neg` vs `¬` has caused bugs requiring DB fixup scripts
- **Before submitting changes**: run `ruff format .` and `ruff check .` for Python; manually smoke-test affected UI flows
