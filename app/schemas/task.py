from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskPriority, TaskStatus



class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.new
    priority: TaskPriority = TaskPriority.medium
    due_date: datetime | None = None
    assignee_id: int | None = None



class TaskCreate(TaskBase):
    pass



class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None



class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)


    id: int
    created_at: datetime
    updated_at: datetime