from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate



def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)



def list_tasks(
    db: Session,
    *,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if assignee_id is not None:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())



def create_task(db: Session, data: TaskCreate) -> Task: 
    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task



def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task



def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()