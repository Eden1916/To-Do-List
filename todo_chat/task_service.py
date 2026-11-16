from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from todo_chat.models import Task
from todo_chat.schema import TaskCreate


def create_task(session: Session, owner_id: int, payload: TaskCreate) -> Task:
    task = Task(owner_user_id=owner_id, **payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def owned_task(session: Session, owner_id: int, task_id: int) -> Task:
    task = session.scalar(select(Task).where(
        Task.id == task_id, Task.owner_user_id == owner_id,
    ))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task
