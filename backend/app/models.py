from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _validate_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be blank")
    if len(stripped) > 200:
        raise ValueError("title must be at most 200 characters")
    return stripped


MAX_TAG_COUNT = 10
MAX_TAG_LENGTH = 30


def _validate_tags(value: list[str]) -> list[str]:
    if len(value) > MAX_TAG_COUNT:
        raise ValueError(f"at most {MAX_TAG_COUNT} tags are allowed")
    trimmed = []
    for tag in value:
        stripped = tag.strip()
        if not stripped:
            raise ValueError("tags must not be blank")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"each tag must be at most {MAX_TAG_LENGTH} characters")
        trimmed.append(stripped)
    return trimmed


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and normalize the title field.

        Args:
            v: The raw title value.

        Returns:
            str: The trimmed title.

        Raises:
            ValueError: If the trimmed title is blank or exceeds 200
                characters (surfaces as a 422 response).
        """
        return _validate_title(v)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize the tags field.

        Args:
            v: The raw list of tag strings.

        Returns:
            list[str]: The trimmed tags, in the same order.

        Raises:
            ValueError: If more than MAX_TAG_COUNT tags are given, any
                tag is blank after trimming, or any tag exceeds
                MAX_TAG_LENGTH characters (surfaces as a 422 response).
        """
        return _validate_tags(v)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize the title field, if provided.

        Args:
            v: The raw title value, or None if title is unset.

        Returns:
            Optional[str]: None if v is None, otherwise the trimmed
                title.

        Raises:
            ValueError: If v is not None and the trimmed title is blank
                or exceeds 200 characters (surfaces as a 422 response).
        """
        if v is None:
            return v
        return _validate_title(v)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate and normalize the tags field, if provided.

        Args:
            v: The raw list of tag strings, or None if tags is unset.

        Returns:
            Optional[list[str]]: None if v is None, otherwise the
                trimmed tags in the same order.

        Raises:
            ValueError: If v is not None and more than MAX_TAG_COUNT
                tags are given, any tag is blank after trimming, or any
                tag exceeds MAX_TAG_LENGTH characters (surfaces as a 422
                response).
        """
        if v is None:
            return v
        return _validate_tags(v)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def overdue(self) -> bool:
        """Whether this task is currently overdue.

        Computed at read/serialization time from due_date and status via
        business_rules.is_overdue — never persisted, so a task can
        become overdue purely from the passage of time without any
        write (see CLAUDE.md).

        Returns:
            bool: True if overdue, False otherwise.
        """
        from app.business_rules import is_overdue

        return is_overdue(self.due_date, self.status)
