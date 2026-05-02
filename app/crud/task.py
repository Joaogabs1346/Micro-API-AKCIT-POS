from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get(db: Session, task_id: int) -> Task | None:
    """Return a single task by its id, or None if not found."""
    return db.get(Task, task_id)


def get_multi(
    db: Session,
    *,
    status: TaskStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    """Return tasks, optionally filtered by status, with pagination."""
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create(db: Session, *, obj_in: TaskCreate) -> Task:
    """Persist a new task and return the stored row."""
    task = Task(
        title=obj_in.title,
        description=obj_in.description,
        status=obj_in.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update(db: Session, *, db_obj: Task, obj_in: TaskUpdate) -> Task:
    """Apply partial updates from the payload to the task and persist."""
    data = obj_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def mark_completed(db: Session, *, db_obj: Task) -> Task:
    """Shortcut to flip a task's status to COMPLETED."""
    db_obj.status = TaskStatus.COMPLETED
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, *, db_obj: Task) -> None:
    """Remove the task from the database."""
    db.delete(db_obj)
    db.commit()
