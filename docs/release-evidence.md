# Release Evidence — Final Project

**Branch:** `final-project`
**Evidence gathered:** 2026-08-20 (Stage 2 baseline verification), with additional CI evidence and a Stage 3 re-verification pass added 2026-08-21 (see §6 and §9)
**Document drafted:** 2026-08-21
**Repository commit at time of evidence:** `725411a` (branch had not diverged from `main` at collection time; still the current `final-project` HEAD as of the 2026-08-21 additions — see §6)

This document records only evidence actually observed while running commands against the application during Stage 2. It does not restate configuration as if it were a runtime result. Where no runtime evidence was collected, that is stated explicitly rather than inferred from what a file appears to do.

---

## 1. Backend test suite

| | |
|---|---|
| **Command** | `venv/Scripts/python.exe -m pytest tests/ -v` (run from `backend/`, equivalent to the documented `pytest tests/ -v` with the project venv activated) |
| **Environment** | Python 3.13.7 (project venv), pytest 9.1.1 |
| **Observed result** | `48 passed, 2 warnings in 0.94s` — 0 failed |
| **Pass/Fail** | **Pass** |
| **Evidence type** | Runtime observation (actual test run) |
| **Notes** | The 2 warnings are pre-existing Starlette/FastAPI deprecation notices (`httpx`/`starlette.testclient` deprecation; `HTTP_422_UNPROCESSABLE_ENTITY` deprecation) — not test failures, not introduced during this stage. `backend/tests/verify_a.py` was not collected (it defines no `test_` functions), consistent with the README's own note that it is not a pytest file. |

## 2. Backend `/health` — local runtime

| | |
|---|---|
| **Startup command** | `uvicorn app.main:app --reload --port 8000` (run from `backend/`, documented command) |
| **Check command** | `curl -s -w "\nHTTP_STATUS:%{http_code}\n" http://127.0.0.1:8000/health` |
| **Observed result** | `HTTP_STATUS:200`, body `{"status":"ok","timestamp":"2026-08-20T22:56:23.463164+00:00"}` |
| **Pass/Fail** | **Pass** |
| **Evidence type** | Runtime observation |

## 3. Frontend runtime verification

Verified by actually driving the running frontend in a headless Chromium browser (Playwright, using browser binaries and a Node module already present on this machine — no project-specific run skill existed for this repo) against the live backend, rather than by reading the HTML/JS source.

| Step | Observed result | Pass/Fail |
|---|---|---|
| Load `http://127.0.0.1:5500/index.html` (served via `python -m http.server 5500`, documented command) | Page rendered: "Task Tracker Kanban" header, **ToDo / InProgress / Done** columns, empty-state message | Pass |
| Click `+ New task`, fill title, submit | Modal opened and submitted without error | Pass |
| Created task appears on board | New task card visible in the **ToDo** column immediately after create | Pass |
| Click `Edit` on the created card, change title, submit | Edit modal opened, accepted the change, submitted without error | Pass |
| Edited task appears on board | Card text updated to the new title | Pass |
| Cross-check via API | `GET http://127.0.0.1:8000/tasks` returned the same task record with the edited title, confirming frontend and backend state agree | Pass |
| JS/console errors during the whole run | Zero `console.error` events, zero uncaught page errors | Pass |

**Evidence type:** Runtime observation (headless browser driving the live page, live API cross-check).

Dev servers (ports 8000 and 5500) were stopped after this check; both ports confirmed free afterward.

## 4. Docker build

| | |
|---|---|
| **Command** | `docker build -t task-tracker:local .` (run from repo root) |
| **Observed result** | Build completed successfully — multi-stage build on `python:3.11-slim`, dependency install step succeeded, final image tagged `task-tracker:local` |
| **Pass/Fail** | **Pass** |
| **Evidence type** | Runtime observation (actual `docker build`) |
| **Notes** | Docker Desktop's engine was not running at the start of this stage; it was started (a change to local running state, not to any file) so this build/run evidence could be collected. |

## 5. Docker container — runtime verification

| Check | Command | Observed result | Pass/Fail |
|---|---|---|---|
| Container starts | `docker run --rm -d -p 8000:8000 task-tracker:local` (documented command is `docker run --rm -p 8000:8000 task-tracker:local`; `-d` added to run detached for scripted verification — same image and port mapping) | `docker ps` showed `Up`, ports `0.0.0.0:8000->8000/tcp` | Pass |
| `/health` in container | `curl -s -w "\nHTTP_STATUS:%{http_code}\n" http://127.0.0.1:8000/health` | `HTTP_STATUS:200`, body `{"status":"ok","timestamp":"2026-08-20T23:08:21.061785+00:00"}` | Pass |
| Runtime user | `docker exec task-tracker-stage2 whoami` | `app` | Pass |
| `.env`/secrets check | `docker exec task-tracker-stage2 find / -maxdepth 3 -iname '*.env*'` | No matches; `/app` contained only the copied `app/` code | Pass |
| Runtime command/user | `docker inspect task-tracker-stage2 --format '{{.Config.Cmd}} \| User={{.Config.User}}'` | `[uvicorn app.main:app --host 0.0.0.0 --port 8000] \| User=app` | Pass (matches Dockerfile's `CMD`) |

**Evidence type:** Runtime observation (all rows — live container, not the Dockerfile read alone).

Container was stopped after verification (`docker stop`); it was run with `--rm` so it self-removed.

## 6. CI evidence

**Workflow file:** `.github/workflows/ci.yml` (not modified as part of this evidence-gathering).

| Item | Evidence |
|---|---|
| Triggers | `push` (`branches: ["**"]` — every branch) and `pull_request` (`branches: ["main"]`) |
| Python version | `actions/setup-python@v5`, `python-version: "3.11"` — an exact pin, not a range, not `latest`, not a matrix |
| Dependency installation | `python -m pip install --upgrade pip` then `pip install -r requirements.txt`, run from the checkout root (no `working-directory` override on that step) |
| Exact test command CI runs | `pytest -v`, with `working-directory: backend` — no `tests/` path argument (README §5 documents `pytest tests/ -v`; both command strings were run again in §9 below and collected the same 48 tests in this repository's current layout) |
| Shortcut check (read `ci.yml` in full, this session) | No `continue-on-error`, no `\|\| true`, no `--exit-zero`, no output redirection around the "Run tests" step. Nothing suppresses a non-zero `pytest` exit code. |
| Actual CI run | **Verified 2026-08-21**, read-only, via GitHub's public Actions UI (`https://github.com/rawadsh/task-tracker/actions` and the run's own page) — `gh` CLI and direct API access were not available in this environment, so this is a rendered-page read, not a raw API call. Run **`CI #5`**, workflow `ci.yml`, job `test`, commit `725411ab2a0e0b544ca0119a7e8532c70469f700`, branch `main`, trigger `push`, **conclusion: success**, ~15s duration. Run URL: `https://github.com/rawadsh/task-tracker/actions/runs/31911960528`. |
| Branch/commit relationship | `git rev-parse HEAD` on `final-project` (re-checked 2026-08-21) returns the same commit, `725411ab2a0e0b544ca0119a7e8532c70469f700` — i.e. the commit with the verified successful run is the exact commit `final-project` currently points to. `git ls-remote --heads origin` (re-checked 2026-08-21) shows only `main`, `ci-proof-red-green`, `mid-course-project` on the remote — **no `final-project` branch exists on GitHub**. The Actions UI's branch list independently shows the same: no runs under a branch named `final-project`. The successful run is attributed to `main` only because that is the sole remote ref currently pointing at this commit — not because CI failed to run, or ran and failed, for this commit. |
| **What this run does *not* cover** | This run corresponds to the commit as it exists on `main`/`final-project`'s current HEAD. The documentation work in this final-project pass — this file, `docs/final-ai-review.md`, and the pending edits to `README.md`/`docs/technical-note.md` — exists only as **uncommitted working-tree changes** as of 2026-08-21 (confirmed via `git status`). None of that has been committed, none has been pushed, and therefore **none of it has been through this or any other CI run**. The green run above is evidence about the application/workflow state at commit `725411ab...`, not evidence that the current uncommitted documentation changes have been CI-verified — they haven't, because they aren't committed. |

**Correction to this document's earlier state:** §7 and §8 below (renumbered from the original §6/§7) previously stated, and `docs/final-ai-review.md` §10 separately stated, that no GitHub Actions run had been queried or inspected, marking CI pass/fail `[VERIFY]`. That was accurate as of the 2026-08-20 Stage 2 collection. It is superseded by the row above, gathered 2026-08-21: an actual, existing run for this exact commit was inspected and found to have succeeded. This is new evidence added to the record, not a reinterpretation of Stage 2's evidence.

## 7. README / documentation claim verification

| Claim | Source | Evidence type | Evidence checked | Verdict |
|---|---|---|---|---|
| Test suite covers "the health/version endpoints" | `README.md` §5 | Source-code/test inspection | `backend/tests/test_health.py` confirmed empty (0 bytes); the actual `pytest -v` run in §1 above collected no test named for `/health`, only `test_version.py` for `/version` | **Pre-existing documentation discrepancy — not introduced by the final project.** |
| `pytest tests/ -v` is the documented test command | `README.md` §5 | Source-code inspection | `.github/workflows/ci.yml` runs `pytest -v` (no `tests/` path argument) from the same `backend` working directory; the local run in §1 used `pytest tests/ -v` and collected 48 tests | **Pre-existing documentation discrepancy — not introduced by the final project.** |
| `/version` returns app version plus installed versions of fastapi, pydantic, uvicorn, and python-dotenv | `README.md` §4 | Runtime observation | `curl -s -w "\nHTTP_STATUS:%{http_code}\n" http://127.0.0.1:8000/version` → `HTTP_STATUS:200`, body `{"app_version":"0.1.0","packages":{"fastapi":"0.140.0","pydantic":"2.13.4","uvicorn":"0.51.0","python-dotenv":"1.2.2"}}` | **Confirmed** — exact command and response are on record from this stage; this is a distinct request/response from the `/health` check in §2, not a substitution for it |
| CORS only allows `http://localhost:5500` / `http://127.0.0.1:5500` | `README.md` §4, `CLAUDE.md` | Source-code inspection + automated test result | `backend/app/main.py:25-28` (`LOCAL_FRONTEND_ORIGINS`) contains exactly these two origins; `main.py:30-36` wires them into `CORSMiddleware`; `test_cors.py::test_options_preflight_returns_cors_headers` (one of the 48 passing tests in §1) exercises the preflight path | **Confirmed by source inspection and automated test — not by a live cross-origin browser request in this stage** |
| Docker image runs as non-root user, no secrets baked in | `README.md` §6 | Runtime observation | See §5 above (`whoami` → `app`; no `.env*` found) | **Confirmed at runtime** |
| Local dev "has been run successfully on 3.12/3.13" (README §2, `[VERIFY]` tag) | `README.md` §2 | Runtime observation | This stage's venv is Python 3.13.7; the full 48-test suite passed under it (§1) | **Confirmed for 3.13** |
| CI passes on this branch | `.github/workflows/ci.yml` | Runtime observation (read-only GitHub Actions UI, 2026-08-21) | See §6 above — an actual run for commit `725411ab...` was inspected and found to have succeeded | **Confirmed for commit `725411ab...`** (see §6). This does not extend to any commit made after this evidence-gathering — see §6's "What this run does not cover" row. |

The two documentation discrepancies noted above were not fixed in this stage — see `docs/technical-note.md` for the same two items logged from the CI/Docker rationale side.

## 8. Out of scope for this stage

- No GitHub Actions run was *triggered* by this evidence-gathering process itself. An existing run (from the earlier `main`-branch push of this exact commit) was inspected read-only on 2026-08-21 — see §6. No workflow was newly executed as part of collecting this evidence.
- No repository files were created, edited, deleted, or renamed by the act of collecting the Stage 2 (2026-08-20) evidence in §1–§5 and §7, or the Stage 3 (2026-08-21) re-verification in §6 and §9 — running tests, `curl`, `docker build`/`run`, and reading the GitHub Actions UI does not itself edit files. `backend/`, `frontend/`, `.dockerignore`, and `CLAUDE.md` remain unmodified throughout this project. `.gitignore` and `AGENTS.md` do carry working-tree edits as of this final-project pass (see current `git diff`) — a `.claude/` entry added to `.gitignore`, and a guardrail wording tightening in `AGENTS.md` — but these were separate governance/config edits, not something that happened as a side effect of the evidence-gathering commands described in this section.
- `docs/final-ai-review.md` was not created in Stage 2; it exists as of this final-project pass and is cross-referenced above.

## 9. Stage 3 re-verification (2026-08-21)

The checks below were re-run, not assumed, during this documentation-remediation pass — to confirm the Stage 2 baseline still holds rather than reusing old numbers. Full detail for each check type is in §1–§5, §2 in particular; this section records that the same checks were repeated today with the same outcomes.

| Check | Command | Result |
|---|---|---|
| Backend tests (README's documented command) | `pytest tests/ -v` (project venv, run from `backend/`) | `48 passed, 2 warnings in 0.56s` — 0 failed, same 48 tests as Stage 2 |
| Backend tests (CI's exact command) | `pytest -v` (same venv, same directory) | `48 passed, 2 warnings in 0.81s` — same 48 tests collected as the command above |
| Local `/health` | `uvicorn app.main:app --port 8000`, then `GET /health` | HTTP `200`, `{"status":"ok","timestamp":"2026-08-21T10:07:22.834626+00:00"}` |
| Docker build | `docker build -t task-tracker:local .` (repo root) | Succeeded (layers served from cache where unchanged; final image tagged `task-tracker:local`) |
| Docker container start | `docker run --rm -d -p 8000:8000 --name task-tracker-verify task-tracker:local` | `docker ps` showed `Up`, port `8000` mapped |
| Docker `/health` | `GET http://127.0.0.1:8000/health` | HTTP `200`, `{"status":"ok","timestamp":"2026-08-21T10:11:40.839592+00:00"}` |
| Docker non-root user | `docker exec task-tracker-verify whoami` | `app` |
| Docker secrets check | `docker exec task-tracker-verify sh -c "find / -maxdepth 3 -iname '*.env*'"` | No matches |
| Docker runtime command/user | `docker inspect task-tracker-verify --format '{{.Config.Cmd}} \| User={{.Config.User}}'` | `[uvicorn app.main:app --host 0.0.0.0 --port 8000] \| User=app` |

Container was stopped after verification (`docker stop task-tracker-verify`); it was run with `--rm` so it self-removed. `docker ps` confirmed no leftover container; ports 8000/5500 confirmed free afterward.

**Frontend — explicitly not re-verified this session.** An attempt was made to re-run the same headless-browser Kanban check as Stage 2 (§3), using Playwright's CLI (`npx playwright`, found to be available). The check did not complete: the `playwright` Node module was not resolvable via `require()` in a standalone script in this environment, and installing anything new was not within this session's approved scope. No frontend file was read, edited, or otherwise touched while attempting this. §3's original 2026-08-20 Playwright-driven evidence stands as the last actual runtime check of the frontend; it is not restated as "verified today" because it was not re-run today.

**Scope note:** none of the checks in this section, and none of the CI evidence in §6, cover the documentation edits made during this same pass (this file, `docs/final-ai-review.md`, `README.md`, `docs/technical-note.md`). Those are working-tree-only changes as of 2026-08-21 and have not been committed, pushed, or run through CI.