from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


@router.get("", response_model=list[TaskRead])
def read_tasks(
    status_filter: TaskStatus | None = Query(
        default=None,
        alias="status",
        description="Filter tasks by status (pending, in_progress, completed)",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    """List tasks, optionally filtering by status."""
    return crud.task.get_multi(db, status=status_filter, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    """Retrieve a single task by its id."""
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return obj


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    payload: TaskCreate, db: Session = Depends(get_db)
) -> TaskRead:
    """Create a new task."""
    return crud.task.create(db, obj_in=payload)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
) -> TaskRead:
    """Update any of a task's fields (title, description, status)."""
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.update(db, db_obj=obj, obj_in=payload)


@router.patch("/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    """Mark a task as completed."""
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.mark_completed(db, db_obj=obj)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a task."""
    obj = crud.task.get(db, task_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.task.remove(db, db_obj=obj)
