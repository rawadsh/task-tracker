# Technical Decision Note: CI Workflow Design

**Status:** Draft
**Module:** Module 4 — Task Tracker
**Scope:** `.github/workflows/ci.yml`. This application has no authentication, no database, and no configured deployment target — nothing below should be read as claiming otherwise.

## 1. Context

Before this module, the project had an automated backend test suite (`backend/tests/`, run via `pytest`) but no mechanism that ran it automatically. `CLAUDE.md`'s "Commands" section documents the pre-existing manual flow: activate a venv from the project root, `pip install -r requirements.txt`, `Copy-Item .env.example .env`, then `Set-Location backend` and run `pytest tests/ -v`. That flow only executes when a developer remembers to run it locally — there was no signal on GitHub itself that a given push or pull request had a passing test suite.

`.github/workflows/ci.yml` was added to close that gap: it runs the same test suite automatically on GitHub's infrastructure, rather than relying solely on local manual testing.

**README.md cross-reference** (exact section names/numbers as currently written in README.md):
- Project/dependency setup: README §3 "Local setup"
- Running the backend: README §4 "Run the app locally"
- Running tests: README §5 "Run tests"
- Docker documentation: README §6 "Run with Docker"
- CI documentation: README §7 "CI workflow summary"

## 2. Decision

The workflow defines one job, `test`, on `runs-on: ubuntu-latest`, with exactly four steps: checkout, set up Python, install dependencies, run tests. Each point below is taken directly from the current contents of `.github/workflows/ci.yml`.

- **Triggers:** the workflow runs on `push`, with a `branches: ["**"]` filter (matches every branch name), and on `pull_request`, with a `branches: ["main"]` filter (only PRs targeting `main`). There is no `workflow_dispatch`, schedule, or any other trigger in the file.
- **Python version:** `actions/setup-python@v5` is configured with `python-version: "3.11"` — an exact pin, not `"3"` or `latest`, and not a matrix. The `Dockerfile` independently uses `FROM python:3.11-slim` for both its `builder` and runtime stages — the same exact minor version as CI. This is a consistency point between the two files; it is not evidence that 3.11 is required by the course. [VERIFY: whether 3.11 is a course requirement, or simply the version this project standardized on]
- **Dependency installation:** `requirements.txt` exists only at the repository root (confirmed on disk — there is no `backend/requirements.txt`). The install step in `ci.yml` has no `working-directory` override, so it runs from the checkout root and installs that same root-level `requirements.txt` via `python -m pip install --upgrade pip` followed by `pip install -r requirements.txt`. This matches README §3 "Local setup," which documents `pip install -r requirements.txt` run from the project root.
- **Test execution:** the "Run tests" step sets `working-directory: backend` and runs `pytest -v`. README §5 documents `Set-Location backend` followed by `pytest tests/ -v` — the same working directory (`backend`), but a different exact command string (README includes a `tests/` path argument; CI does not). Both commands have actually been run against this repository during this project and both collected the same 48 tests from `backend/tests/` — this is based on real command executions performed and observed in this session, not assumed.
- **Failure behavior:** `ci.yml` contains no `continue-on-error`, no `|| true`, no `--exit-zero`, and no output piping around the `pytest -v` step. `pytest`'s exit code is therefore the step's (and job's) exit code.
- **Observed CI run evidence:** during this project, a commit that broke a test assertion produced a GitHub Actions run with conclusion `failure`, and a subsequent revert commit on the same branch produced a run with conclusion `success` — both checked directly against the GitHub Actions API in this session. This is real, observed evidence that the workflow's failure behavior (no error-suppression) actually results in failed runs, not just a theoretical reading of the YAML.
- **Deployment boundary:** the job has no build, push, publish, or deploy step of any kind. This workflow is test verification only; it does not deploy the application anywhere, and no deployment target exists in this repository.
- **Docker relationship:** `ci.yml` contains no Docker commands — it does not build, run, or reference the `Dockerfile` in any way. CI and Docker are independent configurations. They happen to agree on the Python version (3.11), which is a useful consistency point, but that agreement is not enforced by any automation — nothing prevents one file from being changed without the other.

## 3. Alternatives Considered

- **Python version matrix (e.g. 3.11–3.13) vs. the single pinned 3.11 that was chosen.** A matrix was not adopted; testing only 3.11 keeps CI aligned with the exact version the `Dockerfile` uses. [VERIFY: whether this leaves a gap the course cares about]
- **Running tests inside the Docker image during CI vs. running `pytest` directly on the runner (chosen).** Running tests directly on the `ubuntu-latest` runner is simpler, and matches the fact that `ci.yml` contains no Docker step of any kind today.
- **CI-only vs. CI+CD (deploy after tests pass).** CI-only was chosen; no deploy step exists in `ci.yml`, consistent with this module not configuring any deployment target.
- **Action version tags (`@v4`, `@v5`) vs. pinning `actions/checkout`/`actions/setup-python` to a specific commit SHA.** Tags were chosen (as currently committed in `ci.yml`); SHA-pinning was raised in an earlier review as a supply-chain-hardening option but has not been applied.

## 4. Trade-offs

DRAFT - REWRITE IN MY OWN WORDS

- Pinning Actions by tag (`@v4`/`@v5`) is easier to read and maintain than a 40-character SHA, but relies on the tag never being repointed to different code. [VERIFY: real-world likelihood of this for `actions/checkout`/`actions/setup-python` specifically]
- Testing only Python 3.11 keeps CI simple and matches the Docker image, but gives no automated signal about behavior on any other Python version.
- Because `ci.yml` never builds the Docker image, nothing in CI automatically catches a broken `Dockerfile` — that has so far only been checked by manually running `docker build`/`docker run` outside of CI.

## 5. Consequences

- Every push (any branch, per the `branches: ["**"]` filter) and every pull request targeting `main` now produces an automatic pass/fail signal from the real test suite, instead of depending on someone remembering to run `pytest` locally.
- This is evidenced, not assumed: an intentionally broken test produced a `failure` run, and its revert produced a `success` run, both confirmed via the GitHub Actions API in this session.
- Whether a failing run actually blocks a merge into `main` depends on GitHub branch protection settings. This cannot be verified from files in this repository. [VERIFY]
- Docker image correctness (build succeeds, `/health` responds, runs as non-root user `app`) has been checked manually in this project via direct `docker build`/`docker run`/`curl` commands, but that check is not repeated automatically by CI on every change.
- No deployment consequence exists, positive or negative, because no deployment step exists in `ci.yml`.

## 6. Open Questions

DRAFT - REWRITE IN MY OWN WORDS

- [VERIFY] Is branch protection enabled on `main` so a failing CI run actually blocks merging, or is the status currently advisory-only?
- [VERIFY] Does the course expect a Python version matrix, or is pinning to exactly 3.11 (matching the Dockerfile) sufficient?
- Is SHA-pinning `actions/checkout`/`actions/setup-python` worth the maintenance cost for a small learning project, versus the current tag-based approach?
- Would a Docker build-only step in CI (no push, no deploy) be a worthwhile smoke check, given the Dockerfile currently has no automated verification at all?

**README inconsistencies found during verification (not fixed here, per instructions not to modify README.md):**
- README §5 documents the run-tests command as `pytest tests/ -v`, while `ci.yml` actually runs `pytest -v` (no path argument). Both were run in this session and collected the same 48 tests, but the two documented command strings differ.
- `backend/tests/test_health.py` is confirmed empty (0 bytes) — `pytest` collects no test for `/health` from it. README §5 currently describes the suite as covering "the health/version endpoints," but only `/version` has an actual test (`test_version.py`).

I would do this differently by...