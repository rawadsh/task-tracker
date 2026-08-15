# Task Tracker — Architecture (Strategy C: targeted context)

## 1. What the app does

The Task Tracker is a FastAPI backend exposing CRUD endpoints for tasks, plus `/health` and `/version` status endpoints. Tasks have a title, description, status, priority, assignee, due date, and tags, and are held in a single in-memory store for the life of the process.

## 2. Data model

Three Pydantic models define the task shape (`app/models.py`):

- **TaskCreate** (POST body) — `title` (required, trimmed, ≤200 chars), `description` (optional, defaults to `""`), `status` (defaults to `ToDo`), `priority` (defaults to `Medium`), `assignee` (optional), `due_date` (optional date), `tags` (list of strings, ≤10 tags, each trimmed and ≤30 chars). Unknown fields are rejected (`extra="forbid"`).
- **TaskUpdate** (PATCH body) — same fields as TaskCreate, all `Optional` with a default of `None`, same `extra="forbid"` and title/tag validation when a value is supplied.
- **TaskResponse** (API output) — adds `id` (string), `created_at`/`updated_at` (datetime), and a computed `overdue` field. `overdue` is a `@computed_field` property, not a stored attribute — derived at read/serialization time from `due_date` and `status` via `is_overdue` (imported from `app.business_rules` at call time). `TaskStatus` (`ToDo`, `InProgress`, `Done`) and `TaskPriority` (`Low`, `Medium`, `High`) are string enums.

Storage (`app/storage.py`) holds exactly one entity: a module-level dict `_tasks: dict[str, TaskResponse]`, keyed by task id.

## 3. Request flow: creating a task

1. Client sends `POST /tasks` with a JSON body.
2. FastAPI parses and validates against `TaskCreate` — unknown fields, a blank/too-long title, or invalid tags fail here with a 422, before the route body runs.
3. `create_task` (`app/main.py`) calls `storage.add_task(payload)` with no other logic.
4. `add_task` generates a UUID4 id, sets `created_at`/`updated_at` to current UTC time, normalizes `description` to `""` if falsy, builds a `TaskResponse`, stores it in `_tasks`, and returns it.
5. FastAPI serializes the returned `TaskResponse`, computing `overdue` during serialization, and responds `201 Created`.

## 4. Key files

- `app/main.py` — FastAPI app, CORS config, and all routes (`/health`, `/version`, `/tasks` CRUD); handlers contain no business logic beyond existence checks and delegating to `storage`.
- `app/models.py` — `TaskCreate`, `TaskUpdate`, `TaskResponse` schemas; `TaskStatus`/`TaskPriority` enums; field-level validation.
- `app/storage.py` — the in-memory `_tasks` dict and CRUD/query functions (`add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`), plus `_reset()`.
- `app/business_rules.py` — referenced by `main.py` (`validate_status_transition`) and `models.py`/`storage.py` (`is_overdue`), but **not read for this doc**.

## 5. Conventions

- **Validation**: shape/field validation lives entirely in `app/models.py` as Pydantic `field_validator`s, enforced before a route body executes.
- **Storage**: a single process-global dict in `app/storage.py`; no database, no persistence across restarts. PATCH uses `model_dump(exclude_unset=True)` — omitted fields untouched, explicit `null`/`[]` overwrites; if nothing was set, task returned unchanged and `updated_at` untouched.
- **Error handling**: `main.py` handlers check for `None` returns and raise `HTTPException(404, ...)` explicitly; Pydantic validation failures surface as 422 automatically.
- **Frontend/backend interaction**: not visible from the files I read.

## 6. Not visible / assumptions

- `is_overdue` and `validate_status_transition` internals — in `app/business_rules.py`, out of scope for this read.
- Frontend behavior — `frontend/index.html` not read.
- Whether other modules touch `storage._tasks` directly — not visible from the files I read.
- Test conventions / `_reset()`'s actual caller — not visible from the files I read.