from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import task as crud_task
from app.crud import user as crud_user
from app.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _ensure_assignee_exists(db: Session, assignee_id: int | None) -> None:
    if assignee_id is not None and crud_user.get_user(db, assignee_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={assignee_id} not found",
        )


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    _ensure_assignee_exists(db, payload.assignee_id)
    return crud_task.create_task(db, payload)


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    status_: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud_task.list_tasks(
        db,
        status=status_,
        priority=priority,
        assignee_id=assignee_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud_task.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = crud_task.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.assignee_id is not None:
        _ensure_assignee_exists(db, payload.assignee_id)
    return crud_task.update_task(db, task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud_task.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    crud_task.delete_task(db, task)