# FILE: app/business_rules.py

from datetime import date
from typing import Optional

from fastapi import HTTPException, status

from app.models import TaskStatus


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    (TaskStatus.TODO, TaskStatus.TODO),
    (TaskStatus.IN_PROGRESS, TaskStatus.IN_PROGRESS),
    (TaskStatus.DONE, TaskStatus.DONE),
})


def validate_status_transition(
    current: TaskStatus,
    new: TaskStatus,
) -> None:
    """Validate that a status change is allowed.

    Same-status transitions (e.g. ToDo -> ToDo) are explicitly allowed —
    see the (TODO,TODO)/(IN_PROGRESS,IN_PROGRESS)/(DONE,DONE) entries in
    VALID_TRANSITIONS, confirmed by
    test_patch_same_status_returns_200_and_keeps_status.

    Args:
        current: The task's current status.
        new: The requested new status.

    Raises:
        HTTPException: 422 if (current, new) is not a member of
            VALID_TRANSITIONS, with a detail message listing the
            allowed transitions.
    """
    # Same-status transitions are explicitly allowed via VALID_TRANSITIONS.
    # Anything not in VALID_TRANSITIONS is invalid.
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted(
            {f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS}
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} "
                f"to {new.value}. Allowed transitions: {allowed}"
            ),
        )


def is_overdue(due_date: Optional[date], status: TaskStatus) -> bool:
    """Determine whether a task counts as overdue.

    A task with no due date is never overdue. A task in DONE status is
    never overdue regardless of due date. Otherwise a task is overdue if
    due_date is strictly before date.today() (server-local time, not
    UTC — timezone-aware due dates are explicitly out of scope per
    mini-adr.md).

    Args:
        due_date: The task's due date, or None if it has none.
        status: The task's current status.

    Returns:
        bool: True if the task is overdue, False otherwise.
    """
    if due_date is None:
        return False
    if status == TaskStatus.DONE:
        return False
    return due_date < date.today()