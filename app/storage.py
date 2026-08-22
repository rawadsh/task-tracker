from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.business_rules import is_overdue
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task from validated input.

    Generates a new UUID4 id and sets created_at/updated_at to the
    current UTC time. `description` is stored as "" if
    payload.description is falsy (None or empty string).

    Args:
        payload: The validated task-creation data.

    Returns:
        TaskResponse: The newly stored task.
    """
    now = datetime.now(timezone.utc)
    task_id = str(uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered by status/priority/overdue/tag.

    Filters are applied independently and combined with AND. The
    `overdue` filter only has an effect when truthy — overdue=False is
    equivalent to omitting it (overdue=false filtering is explicitly out
    of scope; see docs/midcourse/mini-adr.md). Tag matching is
    exact-match and case-sensitive against membership in each task's
    `tags` list.

    Args:
        status: Exact status to filter by, or None for no filter.
        priority: Exact priority to filter by, or None for no filter.
        overdue: If truthy, only return tasks where
            business_rules.is_overdue(task.due_date, task.status) is
            True. Falsy values apply no overdue filtering.
        tag: Exact, case-sensitive tag to filter by, or None for no
            filter.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if overdue:
        tasks = [task for task in tasks if is_overdue(task.due_date, task.status)]
    if tag is not None:
        tasks = [task for task in tasks if tag in task.tags]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by id.

    Args:
        task_id: The task's id.

    Returns:
        Optional[TaskResponse]: The task if it exists, otherwise None.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Uses payload.model_dump(exclude_unset=True) so only fields
    explicitly present in the request are changed; omitted fields are
    left as-is, while an explicit null/[] overwrites the existing value.
    If no fields were set on payload, the task is returned unchanged and
    updated_at is not touched.

    Args:
        task_id: The id of the task to update.
        payload: The fields to change; unset fields are ignored.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task
            exists with the given task_id.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    updates["updated_at"] = datetime.now(timezone.utc)
    updated_task = task.model_copy(update=updates)
    _tasks[task_id] = updated_task
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a stored task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        bool: True if a task was found and deleted, False if no task
            existed with the given task_id.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
