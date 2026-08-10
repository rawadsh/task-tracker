# Task Tracker

## 1. Project overview

A small, in-memory Task Tracker API built with FastAPI and Pydantic, with a
static vanilla-JS/HTML frontend. It started as the Module 1 project of an
AI-assisted development course (see `docs/midcourse/`) and has since been
extended through Module 4 [VERIFY: module numbering per your course — not
documented in-repo] with a GitHub Actions CI workflow and a Dockerfile for
local containerized runs.

This module does not add deployment, authentication, or a database — see
[Project conventions and current limitations](#9-project-conventions-and-current-limitations).

Current features:
- Task CRUD, status and priority handling
- Optional due dates and backend-computed, never-persisted overdue status
- Overdue-only filtering (`overdue=true`)
- Task tags with exact, case-sensitive filtering
- Browser-based frontend
- Automated backend tests and CI enforcement

## 2. Prerequisites

- Python 3.11 or newer
  ([VERIFY]: CI and the Dockerfile pin exactly 3.11; local dev has been run
  successfully on 3.12/3.13 too, but 3.11 is the only version proven in CI)
- `pip` (bundled with Python)
- Git
- Docker Desktop — only needed for [Run with Docker](#6-run-with-docker)

## 3. Local setup

From the project root:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

> `requirements.txt` uses minimum-version (`>=`) constraints, not pins.
> After installing, run `pip freeze` to see the resolved versions.

## 4. Run the app locally

The app package lives at `backend/app`, so move into `backend/` before
starting uvicorn (venv stays activated regardless of working directory):

```powershell
Set-Location backend
uvicorn app.main:app --reload --port 8000
```

The API is available at http://127.0.0.1:8000 — Swagger UI at `/docs`,
ReDoc at `/redoc`.

Quick checks, from a second terminal:

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/version
```

`/health` returns `{"status": "ok", "timestamp": "..."}`. `/version` returns
the app version plus installed versions of fastapi, pydantic, uvicorn, and
python-dotenv.

To also run the frontend, from the project root in another terminal:

```powershell
Set-Location frontend
python -m http.server 5500
```

CORS is only configured for `http://localhost:5500` / `http://127.0.0.1:5500`
— serving the frontend on a different port will get its requests blocked.

## 5. Run tests

```powershell
Set-Location backend
pytest tests/ -v
```

Runs the complete backend suite: task CRUD, status/priority, due dates,
overdue filtering, tags and tag filtering, CORS behavior, and the
health/version endpoints.

Run one feature's tests:

```powershell
pytest tests/test_due_dates.py -v
pytest tests/test_tags.py -v
```

Run a single test:

```powershell
pytest tests/test_tasks.py::test_name -v
```

## 6. Run with Docker

From the project root:

```powershell
docker build -t task-tracker:local .
docker run --rm -p 8000:8000 task-tracker:local
```

Then check http://127.0.0.1:8000/health. The image is a multi-stage build
on `python:3.11-slim`, runs as a non-root `app` user, and starts
`uvicorn app.main:app --host 0.0.0.0 --port 8000` (no `--reload`).
`.env` is excluded via `.dockerignore` — no secrets are baked into the
image; the app runs on its defaults (`APP_ENV=development`) unless you pass
`-e` flags to `docker run`. This module does not configure a deployment
target — the image is for local use only.

## 7. CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and on `pull_request`
targeting `main`:

- Checks out the repo (`actions/checkout@v4`)
- Sets up Python **3.11** exactly (`actions/setup-python@v5`)
- Installs dependencies from the repo root:
  `python -m pip install --upgrade pip` then `pip install -r requirements.txt`
- Runs `pytest -v` with `working-directory: backend`

There are no deployment, build-and-push, or publish steps — CI only
validates that the test suite passes.

## 8. Project structure

```text
task-tracker/
  .gitignore
  .dockerignore
  Dockerfile
  README.md
  CLAUDE.md
  requirements.txt
  .env.example
  .github/
    workflows/
      ci.yml
  backend/
    app/
      __init__.py
      main.py
      models.py
      storage.py
      business_rules.py
    tests/
      conftest.py
      test_cors.py
      test_due_dates.py
      test_health.py
      test_tags.py
      test_tasks.py
      test_version.py
      verify_a.py        # [VERIFY] standalone script, not collected by pytest
  frontend/
    index.html
  docs/
    midcourse/
      user-stories.md
      mini-adr.md
      verification.md
      prompt-log.md
      reflection.md
```

## 9. Project conventions and current limitations

- **Layering**: `main.py` (routes only) → `business_rules.py` (cross-field
  rules) → `storage.py` (persistence); field-level validation lives in
  `models.py` as Pydantic `field_validator`s. See `CLAUDE.md` for the full
  convention.
- **PATCH semantics**: `TaskUpdate` uses `model_dump(exclude_unset=True)` —
  an omitted field is left untouched; an explicit `null`/`[]` overwrites it.
- **Overdue is never persisted** — it's a `@computed_field` recomputed from
  `due_date` + `status` on every read.
- **Tag filtering** is single-value, exact-match, and case-sensitive — no
  partial or case-insensitive matching (see `docs/midcourse/mini-adr.md`).
- **Storage is in-memory only** — a single process-level dict. All data is
  lost on restart; there is no database.
- **No authentication** is implemented, and no database is used.
- **Not production-ready**: no persistence, no auth, no deployment
  configuration. Scope is local development, automated tests, CI
  validation, and a local Docker image only.
- [VERIFY] `business_rules.py`'s inline comment above `VALID_TRANSITIONS`
  ("Same -> same is invalid") contradicts the set's actual contents and
  test coverage — same-status transitions are allowed. See the function's
  docstring.
- [VERIFY] `backend/tests/verify_a.py` is a standalone script not collected
  by `pytest`; its intended purpose isn't documented anywhere in the repo.

## 10. Decision record

Design decisions and rejected alternatives for the due-dates and tags
features are recorded in
[`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md). Related process
docs: [`user-stories.md`](docs/midcourse/user-stories.md),
[`verification.md`](docs/midcourse/verification.md),
[`prompt-log.md`](docs/midcourse/prompt-log.md),
[`reflection.md`](docs/midcourse/reflection.md).