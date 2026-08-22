import os
from datetime import datetime, timezone
from importlib.metadata import version as _pkg_version

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 learning project — in-memory Task Tracker.",
    version="0.1.0",
)

TRACKED_PACKAGES = ("fastapi", "pydantic", "uvicorn", "python-dotenv")

LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health() -> dict:
    """Report basic service liveness.

    Returns:
        dict: A static "status" of "ok" plus the current UTC timestamp
            in ISO 8601 format.

    Example:
        GET /health
        -> {"status": "ok", "timestamp": "2026-08-10T00:03:24.088310+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version")
def get_version() -> dict:
    """Report the running app version and tracked dependency versions.

    Looks up installed package versions for TRACKED_PACKAGES via
    importlib.metadata, so the response reflects what's actually
    installed rather than what's pinned in requirements.txt.

    Returns:
        dict: "app_version" (the FastAPI app's version string) and
            "packages" (tracked package name -> installed version).

    Example:
        GET /version
        -> {"app_version": "0.1.0", "packages": {"fastapi": "0.141.1", ...}}
    """
    return {
        "app_version": app.version,
        "packages": {name: _pkg_version(name) for name in TRACKED_PACKAGES},
    }


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, overdue, or tag.

    All supplied filters are combined with AND.

    Args:
        status: Only return tasks with this exact status; omit for all.
        priority: Only return tasks with this exact priority; omit for all.
        overdue: Only meaningful when True — returns tasks for which
            business_rules.is_overdue(due_date, status) is True. Passing
            False behaves the same as omitting it; overdue=false
            filtering is explicitly out of scope (see mini-adr.md).
        tag: Only return tasks whose `tags` list contains this exact
            string. Matching is single-value, exact, and case-sensitive.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters.

    Example:
        GET /tasks?status=ToDo&tag=backend
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by id.

    Args:
        task_id: The task's unique id (a UUID4 string).

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task exists with the given task_id.

    Example:
        GET /tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload: The task fields to create. Unknown fields are rejected
            with 422 (extra="forbid"). `status` defaults to ToDo and
            `priority` to Medium if omitted.

    Returns:
        TaskResponse: The newly created task, including its generated
            id, timestamps, and computed `overdue` flag.

    Example:
        POST /tasks
        {"title": "Write docs", "priority": "High"}
    """
    return storage.add_task(payload)


# PATCH ROUTE ONLY FROM app/main.py

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task (PATCH semantics).

    Only fields explicitly present in the request body are changed; an
    omitted field leaves the existing value untouched, while an explicit
    null/[] overwrites it (e.g. tags: [] clears tags, omitting tags
    preserves them — see storage.update_task).

    If `status` is included, the transition from the task's current
    status to the new one is validated via
    business_rules.validate_status_transition before the update is
    applied; an invalid transition raises 422 and the task is not
    modified.

    Args:
        task_id: The id of the task to update.
        payload: The fields to change. Unknown fields are rejected with
            422 (extra="forbid").

    Returns:
        TaskResponse: The task after applying the update.

    Raises:
        HTTPException: 404 if no task exists with the given task_id.
        HTTPException: 422 if `status` is supplied and the transition is
            not in business_rules.VALID_TRANSITIONS (same-status
            transitions, e.g. ToDo -> ToDo, are allowed).

    Example:
        PATCH /tasks/{task_id}
        {"status": "InProgress"}
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {task_id} not found",
            )

        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
)
def delete_task(task_id: str) -> None:
    """Delete a task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        None: On success, responds with 204 No Content and an empty body.

    Raises:
        HTTPException: 404 if no task exists with the given task_id.

    Example:
        DELETE /tasks/{task_id}
    """
    if storage.delete_task(task_id):
        return

    raise HTTPException(
        status_code=404,
        detail=f"Task with id {task_id} not found",
    )