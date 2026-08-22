# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What this is

A small learning-project Task Tracker: a FastAPI + Pydantic backend with an in-memory store, and a single-file vanilla JS/HTML frontend (Kanban-style board). Built as Module 1 of an AI-assisted development course — see `docs/midcourse/` for the assignment's design record and process log.

## Commands

Set up the venv and install dependencies from the project root; run the server and tests from the project root with that same venv activated (`venv\Scripts\Activate.ps1` on Windows).

```powershell
# Setup (first time, from project root)
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

# Run the API (http://127.0.0.1:8000, docs at /docs, /redoc)
uvicorn app.main:app --reload --port 8000

# Run all tests
pytest tests/ -v

# Run one feature's tests
pytest tests/test_due_dates.py -v
pytest tests/test_tags.py -v

# Run a single test
pytest tests/test_tasks.py::test_name -v
```

Frontend is static and served separately (no build step):

```powershell
Set-Location frontend
python -m http.server 5500
```

The backend's CORS config only allows `http://localhost:5500` / `http://127.0.0.1:5500` as frontend origins (`app/main.py`) — if you serve the frontend on a different port, requests will be blocked.

`requirements.txt` uses minimum-version (`>=`) constraints, not pins. After installing, `pip freeze` shows the resolved versions.

## Architecture

Backend is a 4-module layered design under `app/`, each with one job:

- **`models.py`** — Pydantic schemas: `TaskCreate` (POST body), `TaskUpdate` (PATCH body, all fields optional), `TaskResponse` (API output). All use `extra="forbid"` so unknown fields 422 instead of being silently dropped. Field-level validation (title trim/length, tag trim/count/length) lives here as `field_validator`s, since it's shape validation of a single field, not cross-field business logic. `TaskResponse.overdue` is a `@computed_field`, not a stored value.
- **`business_rules.py`** — cross-field/domain rules that don't belong on a single field: status-transition legality (`validate_status_transition`) and the overdue predicate (`is_overdue`). Both `models.py` (computed field) and `storage.py` (the `overdue=true` filter) call `is_overdue` so there is exactly one definition of "overdue."
- **`storage.py`** — the entire persistence layer: a single in-memory `dict[str, TaskResponse]` module-level global. No database. All state is lost on process restart. `_reset()` exists solely for test isolation (see `tests/conftest.py`'s autouse fixture).
- **`main.py`** — FastAPI routes only; no business logic beyond wiring. Route handlers validate existence/transitions via `storage`/`business_rules` and translate failures to `HTTPException`s.

This layering (route → business rule → storage, with Pydantic doing field validation) is the convention to follow for any new field or endpoint: shape validation goes in `models.py`, cross-field/domain rules go in `business_rules.py`, and `main.py` stays thin.

**PATCH semantics**: `TaskUpdate` fields are optional and updates use `model_dump(exclude_unset=True)` in `storage.update_task` — an omitted field leaves the existing value untouched, but an explicit `null`/`[]` overwrites it (e.g. `tags: []` clears tags; omitting `tags` preserves them). Keep this distinction in mind when adding new updatable fields.

**Overdue** is deliberately never stored — it's recomputed from `due_date` + `status` at read time, so a task can become overdue purely from the passage of time without any write happening. Don't reintroduce it as a persisted field.

Frontend (`frontend/index.html`) is a single static file with inline CSS/JS — no framework, no build tooling. It renders whatever the backend returns (e.g. `due_date`/`overdue`) rather than recomputing derived values client-side; keep that split (backend owns derived state, frontend is a thin renderer) when extending the UI.

## Testing conventions

- `tests/conftest.py` provides an autouse `_reset_storage` fixture that clears the in-memory store before and after every test — tests never need to manage cleanup themselves, but also can't assume any task exists unless they create it.
- Tests use FastAPI's `TestClient` via the `client` fixture, and a `created_task` fixture for tests that need an existing task to act on.
- Test files are organized by feature (`test_tasks.py`, `test_due_dates.py`, `test_tags.py`, `test_cors.py`), not by layer — add new feature tests as a new `test_<feature>.py` rather than appending to an unrelated file.

## Docs

`docs/midcourse/` contains the process artifacts for this course module: `mini-adr.md` (design decisions and rejected alternatives for the due-dates and tags features), `user-stories.md`, `verification.md`, `prompt-log.md`, and `reflection.md`. Consult `mini-adr.md` before changing due-date or tag behavior — it records what was explicitly scoped out (e.g. `overdue=false` filtering, tags as a separate entity, case-insensitive tag dedup) and why.


## Do not
- Do no add authentication 
- Do not introduce a database without  asking
- Do not change public response shapes without explicit approval
- Do not remove tests to make CI pass
- Do not run destructive shell commands without explicit confirmation 
- Do not use always allow for broad shell permissions

@README.md

## Module 5 governance guardrails

This repository is being used for AI-Assisted Coding Module 5 governance,
not feature development.

- Work on one bounded task per Codex task.
- Start read-only: inspect relevant files before making repository claims or
  proposing changes.
- Prefer documentation work first. Edit only `docs/` by default.
- Do not modify `app/` or `frontend/` unless the user explicitly approves one
  specific, minimal fix.
- Before editing any file, show the exact proposed change and obtain explicit
  approval.
- Cite the actual files inspected for every repository claim. If a file is
  unavailable or evidence is incomplete, say **not confirmed** rather than
  guessing from framework conventions.
- Do not invent findings from an “AI-Assisted Coding - Module 5 Prompt
  Library.” Treat such findings as **not confirmed** unless the relevant
  library file was inspected in the current task.

## Security and evidence reminders

- Never paste, expose, log, commit, or echo secrets, including `.env` values,
  access tokens, API keys, credentials, or private URLs.
- Do not run destructive commands or irreversible Git operations without
  explicit user confirmation.
- Do not remove tests merely to make checks pass.
- Keep verified evidence separate from assumptions, and identify unverified
  claims as **not confirmed**.
