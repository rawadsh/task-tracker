# Task Tracker — Architecture (Draft A)

## 1. What the app does
Task Tracker is a small in-memory task-management app: a FastAPI backend exposes CRUD endpoints for tasks (with status, priority, optional due date, and tags), and a single-file vanilla JS/HTML frontend renders them as a Kanban board. There is no database, authentication, or deployment config — it's a learning project (course Module 1, extended through Module 4 with CI and Docker).

## 2. Data model
Single entity: **Task** (`backend/app/models.py`).
- `id` — UUID4 string, server-generated
- `title` — required, trimmed, 1–200 chars
- `description` — optional string, defaults to `""`
- `status` — enum `ToDo | InProgress | Done`
- `priority` — enum `Low | Medium | High`
- `assignee` — optional string
- `due_date` — optional date
- `tags` — list of strings, trimmed, max 10 tags, max 30 chars each
- `created_at` / `updated_at` — UTC timestamps, server-set
- `overdue` — **computed, never stored**; derived from `due_date` + `status` at read time (`business_rules.is_overdue`)

Separate schemas per direction: `TaskCreate` (POST body), `TaskUpdate` (PATCH body, all fields optional), `TaskResponse` (API output, includes `overdue`). All use `extra="forbid"` — unknown fields → 422.

## 3. Request flow — creating a task
1. Frontend `POST`s JSON to `{API_BASE}/tasks` (`frontend/index.html`).
2. FastAPI route `create_task` (`main.py`) parses/validates the body as `TaskCreate` — Pydantic runs field validators (title trim/length, tag trim/count/length); violations → 422 automatically.
3. Route calls `storage.add_task(payload)`.
4. `storage.add_task` generates a UUID4 id, sets `created_at`/`updated_at` to now (UTC), builds a `TaskResponse`, and stores it in the module-level in-memory dict.
5. `TaskResponse` is serialized back to the client; `overdue` is computed on the fly during serialization. Response: `201 Created` + the new task.

## 4. Key files
- `backend/app/main.py` — FastAPI routes only (health, version, task CRUD); no business logic beyond wiring.
- `backend/app/models.py` — Pydantic schemas (`TaskCreate`/`TaskUpdate`/`TaskResponse`) and field-level validation.
- `backend/app/business_rules.py` — cross-field rules: status-transition legality and the `is_overdue` predicate (single source of truth).
- `backend/app/storage.py` — entire persistence layer: one in-memory `dict[str, TaskResponse]`; `_reset()` for test isolation only.
- `frontend/index.html` — single static file, inline CSS/JS, Kanban UI; thin renderer of backend data.
- `backend/tests/conftest.py` — autouse fixture resetting storage before/after every test.
- `requirements.txt` — minimum-version (`>=`) dependency constraints, not pins.
- `.github/workflows/ci.yml` — runs `pytest -v` on push/PR against Python 3.11.
- `docs/midcourse/mini-adr.md` — design decisions/rejected alternatives for due-dates and tags.

## 5. Conventions
- **Layering**: route (`main.py`) → business rule (`business_rules.py`) → storage (`storage.py`); field-shape validation lives in `models.py` as `field_validator`s. New fields/endpoints should follow this split.
- **Validation**: Pydantic handles shape/field rules (raises `ValueError` → FastAPI 422); domain rules (status transitions, overdue) are explicit functions in `business_rules.py`, invoked from routes/storage.
- **Storage**: single process-level in-memory dict, no persistence across restarts, no database.
- **PATCH semantics**: `model_dump(exclude_unset=True)` — omitted field leaves value untouched; explicit `null`/`[]` overwrites it.
- **Error handling**: routes translate storage/business-rule failures (not-found, invalid transition) into `HTTPException` (404/422); no global exception handler observed.
- **Frontend/backend interaction**: frontend calls a hardcoded `API_BASE` (`http://127.0.0.1:8000`) via `fetch`; CORS restricts allowed origins to `localhost:5500`/`127.0.0.1:5500`. Frontend renders backend-computed fields (e.g. `overdue`) rather than recomputing them.

## 6. Not visible / assumptions
- Did not open every test file or `docs/midcourse/*` in full — feature scope details (e.g. exact tag-filter edge cases) are asserted from `main.py`/`storage.py` docstrings, not independently verified against tests.
- `backend/tests/verify_a.py` exists but its purpose is undocumented in-repo ([VERIFY] per README) — not covered here.
- Did not inspect `.env.example` or `requirements.txt` contents in detail; "min-version, not pinned" is taken from README/CLAUDE.md, not independently confirmed by reading the file.
- Assumed no authentication/deployment layer exists beyond what CLAUDE.md/README state — did not search for hidden auth middleware.