# Task Tracker

A small learning-project Task Tracker API built with FastAPI and Pydantic. Module 1 of an AI-assisted development course.

## Status
Module 1 skeleton — only a `/health` endpoint is implemented. CRUD, persistence, and the frontend are added in later tasks.

## Requirements
- Python 3.11 or newer
- `pip` (bundled with Python)

## Setup

From the project root:

```powershell
Set-Location backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
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

## Interactive API docs (Swagger)

Open **http://127.0.0.1:8000/docs** in your browser.
Redoc UI is also available at http://127.0.0.1:8000/redoc.

## Project structure

```
task-tracker/
  .gitignore
  README.md
  backend/
    .env.example
    requirements.txt
    app/
      __init__.py
      main.py
```

## What comes next

- CRUD endpoints for tasks
- Simple web frontend (later module)
- Persistence layer (later module — see ADR-0001)