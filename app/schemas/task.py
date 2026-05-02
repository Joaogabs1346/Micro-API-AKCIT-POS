from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Shared fields used both on input and output schemas."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        default=None, description="Optional longer description of the task"
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Current status of the task"
    )


class TaskCreate(TaskBase):
    """Payload accepted when creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Payload accepted when updating a task — all fields are optional."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None


class TaskRead(TaskBase):
    """Payload returned to the client for any task."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
