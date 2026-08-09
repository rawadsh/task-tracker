# Task Tracker

A small learning-project Task Tracker API built with FastAPI and Pydantic. Module 1 of an AI-assisted development course.

## Status
Task Tracker implementation completed for the current module, including:

- Task CRUD operations
- Status and priority handling
- Due dates and backend-computed overdue status
- Overdue filtering
- Task tags and exact/case-sensitive tag filtering
- Web frontend
- Automated backend tests

## Requirements
- Python 3.11 or newer
- `pip` (bundled with Python)

## Setup

## Run the application

### Start the backend

From the project root, set up the virtual environment and install dependencies:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
Set-Location backend
```

> **Version pins:** `requirements.txt` uses minimum-version constraints. After the first install, verify the resolved versions with `pip freeze`. Replace `requirements.txt` with `pip freeze > requirements.txt` if you want fully reproducible installs.

## Run

From `backend/` with the venv activated:

```powershell
uvicorn app.main:app --reload --port 8000
```

The server starts at http://127.0.0.1:8000.

## Test the /health endpoint

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected response shape (timestamp will differ):

```json
{ "status": "ok", "timestamp": "2026-07-25T20:15:00.123456+00:00" }
```

## Test the /version endpoint

```powershell
curl.exe http://127.0.0.1:8000/version
```

Returns the app version and the installed versions of the core runtime dependencies (fastapi, pydantic, uvicorn, python-dotenv).

## Open the frontend

With the backend running, open a second terminal from the project root and start a simple HTTP server for the frontend:

Set-Location frontend
python -m http.server 5500

## Run the tests

From the backend/ directory with the virtual environment activated:

pytest tests/ -v

This runs the complete backend test suite, including tests for:

task CRUD operations
status and priority
due dates
overdue filtering
tags and tag filtering
CORS behavior

## To run a specific feature's tests:

pytest tests/test_due_dates.py -v
pytest tests/test_tags.py -v

## Interactive API docs (Swagger)

Open **http://127.0.0.1:8000/docs** in your browser.
Redoc UI is also available at http://127.0.0.1:8000/redoc.

## Project structure

```text
task-tracker/
  .gitignore
  README.md
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
      test_cors.py
      test_tasks.py
      test_due_dates.py
      test_tags.py
  frontend/
    index.html
  docs/
    midcourse/
      user-stories.md
      mini-adr.md
      verification.md
      prompt-log.md
      reflection.md

```markdown
## Current features

The application currently supports:

- Creating, editing, viewing, and deleting tasks
- Task status and priority
- Optional due dates
- Backend-computed overdue status
- Overdue-only filtering
- Comma-separated task tags
- Tag trimming and backend validation
- Exact, case-sensitive tag filtering
- Combining tag and overdue filters
- Browser-based task management