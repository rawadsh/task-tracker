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

## Final Project

**Branch reviewed:** `final-project`

### What this submission demonstrates

- The existing Task Tracker application still runs within the course's
  intended scope (in-memory storage, no auth, no database) — see
  [Project conventions and current limitations](#9-project-conventions-and-current-limitations).
- `.github/workflows/ci.yml` is configured to run the backend `pytest`
  suite on every `push` and on every `pull_request` targeting `main`. A
  specific run of that workflow, for the exact commit at this branch's
  current HEAD, has been verified as successful — see
  [Known open items](#known-open-items) for the run link and the
  important limits on what that verification does and doesn't cover.
- The Docker image builds and runs, and its `/health` endpoint returns
  `200` from inside the running container.
- AI-assisted work, a dual-track AI/manual security review, and an
  ownership statement are recorded under `docs/` — see
  [Evidence files](#evidence-files) below.

### How to run locally

The exact commands already documented in [§3 Local setup](#3-local-setup)
and [§4 Run the app locally](#4-run-the-app-locally) above, confirmed
working in `docs/release-evidence.md`:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

```powershell
Set-Location backend
uvicorn app.main:app --reload --port 8000
```

### How to run tests

From `backend/`:

```powershell
pytest tests/ -v
```

This is the command documented in [§5 Run tests](#5-run-tests) and the
one actually run to produce the `48 passed, 2 warnings, 0 failed` result
recorded in `docs/release-evidence.md`. Note: `.github/workflows/ci.yml`
runs `pytest -v` (no `tests/` path argument) from the same `backend`
working directory. In this repository's current test layout, both
commands were observed to collect the same 48 tests
(`docs/release-evidence.md` §1, §7, and §9) — that is a statement about this
specific working directory and test layout, not a claim that the two
command strings are interchangeable in general.

### How to run with Docker

The exact commands documented in [§6 Run with Docker](#6-run-with-docker)
above, confirmed working in `docs/release-evidence.md`:

```powershell
docker build -t task-tracker:local .
docker run --rm -d -p 8000:8000 task-tracker:local
```

Then check `http://127.0.0.1:8000/health` — verified in
`docs/release-evidence.md` to return `200`, with the container running
as the non-root `app` user and no `.env`/secrets present inside the image.

### Evidence files

- [`docs/release-evidence.md`](docs/release-evidence.md) — baseline
  test/health/frontend/Docker evidence actually observed for this
  final-project stage.
- [`docs/final-ai-review.md`](docs/final-ai-review.md) — AI security
  findings, manual findings, grading, and an ownership statement.
- [`docs/ai-playbook.md`](docs/ai-playbook.md) — personal AI usage rules
  and a Decision Card.

### AI assistance summary

AI assistance (Claude Code, and ChatGPT for early planning per
`docs/midcourse/reflection.md`) was used across this project for
documentation drafting, CI/Docker rationale (`docs/technical-note.md`),
a dual-track AI-plus-manual security review (`docs/security-review.md`),
and a context-engineering comparison (`docs/architecture.md`). AI output
was not accepted as-is: claimed bugs, fixes, and findings were checked
against the actual file or reproduced before being recorded
(`docs/ai-usage.md`, `docs/final-ai-review.md`). For example, during the
mid-course due-dates feature work, an AI-drafted user story described
overdue tasks as needing "urgent attention" — this wording was rejected
because that benefit had not been requested (`docs/midcourse/prompt-log.md`,
Feature 1 prompt log). That rejection happened earlier in the course, not
during this final-project stage. For this final-project stage
specifically, the baseline claims above were verified by actually running
the test suite, the app, and the Docker container — not by re-reading
code alone — see `docs/release-evidence.md`.

### Known open items

- A successful GitHub Actions run is confirmed for the exact commit at
  `final-project`'s current HEAD (`725411ab2a0e0b544ca0119a7e8532c70469f700`)
  — verified read-only via GitHub's public Actions UI on 2026-08-21: run
  `https://github.com/rawadsh/task-tracker/actions/runs/31911960528`,
  workflow `ci.yml`, conclusion `success`. Full detail in
  `docs/release-evidence.md` §6.
- GitHub attributes that run to `main`, not to `final-project`, because no
  `final-project` branch has ever been pushed to the remote (confirmed via
  `git ls-remote --heads origin` on 2026-08-21 — the remote has `main`,
  `ci-proof-red-green`, and `mid-course-project` only). No run exists under
  a branch named `final-project`.
- That verified run covers the application/workflow state at commit
  `725411ab...`. It does **not** cover the documentation work done during
  this final-project remediation pass (this file, `docs/release-evidence.md`,
  `docs/final-ai-review.md`, `docs/technical-note.md`): as of 2026-08-21
  those exist only as uncommitted working-tree changes and have not been
  committed, pushed, or run through CI.
- The brief's separate requirement for 3 AI code-review comments graded
  Useful/Noise/Wrong is satisfied by the "AI code review mini-log" in
  `docs/final-ai-review.md`.
- Not every requirement in the Final Course Project Brief is claimed
  complete by this section.