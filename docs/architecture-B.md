# Task Tracker — Architecture (Doc B)

## 1. What the app does
A small learning-project Task Tracker: a FastAPI + Pydantic backend with an
in-memory store, paired with a single-file vanilla JS/HTML frontend
(Kanban-style board). Built as a course module in AI-assisted development.
[Source: AGENTS.md]

## 2. Data model
Single entity, **Task**, defined across three Pydantic models in `models.py`:
- `id` (str, UUID4, server-generated)
- `title` (str, trimmed, 1–200 chars, required)
- `description` (str, defaults to `""`)
- `status` (enum: `ToDo` | `InProgress` | `Done`, defaults `ToDo`)
- `priority` (enum: `Low` | `Medium` | `High`, defaults `Medium`)
- `assignee` (optional str)
- `due_date` (optional date)
- `tags` (list[str], max 10 tags, each trimmed and ≤30 chars)
- `created_at` / `updated_at` (datetime, server-set)
- `overdue` (bool, `@computed_field` — never stored; derived from
  `due_date` + `status` at read time via `business_rules.is_overdue`)

`TaskCreate` (POST body) and `TaskUpdate` (PATCH body, all fields optional)
both use `extra="forbid"`, so unknown fields return 422 instead of being
silently dropped. [Source: models.py]

## 3. Request flow — creating a task
1. Client sends `POST /tasks` with a JSON body.
2. FastAPI parses it into `TaskCreate`; Pydantic runs field validators
   (title trim/blank/length check, tags trim/count/length check) and
   rejects unknown fields — failures return 422 before the route body runs.
3. `main.create_task` calls `storage.add_task(payload)`.
4. `storage.add_task` generates a UUID4 id, sets `created_at`/`updated_at`
   to the current UTC time, builds a `TaskResponse`, and stores it in the
   in-memory `_tasks` dict.
5. The response is serialized, computing `overdue` on the fly, and returned
   with `201 Created`. [Source: main.py, storage.py, models.py]

## 4. Key files
- `backend/app/main.py` — FastAPI routes only; translates storage/business-rule failures into `HTTPException`s.
- `backend/app/models.py` — Pydantic schemas (`TaskCreate`/`TaskUpdate`/`TaskResponse`) and field-level validation.
- `backend/app/business_rules.py` — cross-field domain rules: status-transition legality and the `is_overdue` predicate.
- `backend/app/storage.py` — entire persistence layer: one in-memory `dict[str, TaskResponse]`; no database.
- `backend/app/__init__.py` — empty (confirmed by inspection).
- `frontend/index.html` — single-file static frontend; renders backend-computed values rather than recomputing them. [Source: AGENTS.md — file itself not inspected]
- `AGENTS.md` / `CLAUDE.md` — agent-facing guidance: architecture, conventions, and "Do not" guardrails.

## 5. Conventions
- **Validation**: shape/field validation (trimming, length, blank checks) lives in `models.py` as `field_validator`s; cross-field/domain rules (status transitions, overdue) live in `business_rules.py`. `main.py` stays thin — routing and existence checks only.
- **Storage**: a single module-level in-memory dict in `storage.py`; state resets on process restart; `_reset()` exists only for test isolation.
- **PATCH semantics**: `TaskUpdate` uses `model_dump(exclude_unset=True)` — an omitted field is left untouched, an explicit `null`/`[]` overwrites it.
- **Error handling**: `main.py` converts `None`/failed-validation results into `HTTPException` — 404 for missing tasks, 422 for invalid status transitions or schema violations.
- **Frontend/backend interaction**: frontend is a thin renderer of whatever the backend returns (e.g. `due_date`, `overdue`); it does not recompute derived values. CORS restricts accepted origins to `http://localhost:5500` / `http://127.0.0.1:5500`. [Source: AGENTS.md, main.py]

## 6. Not visible / assumptions
- `frontend/index.html` was **not inspected** in this task — its description above comes from AGENTS.md, not direct reading.
- `tests/` and `docs/midcourse/` were **not inspected** — not confirmed.
- The "AI-Assisted Coding - Module 5 Prompt Library" mentioned in the task prompt was **not inspected**; per AGENTS.md's governance guardrails, no findings are attributed to it — **not confirmed**.
- `business_rules.py`'s inline comment above `VALID_TRANSITIONS` is internally consistent with the docstring in the version inspected (same-status transitions are explicitly allowed) — no contradiction found in this file as currently written.