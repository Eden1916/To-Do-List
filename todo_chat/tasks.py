from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from todo_chat.database import get_session
from todo_chat.models import Task, User
from todo_chat.schema import (
    MessageResponse, TaskCreate, TaskList, TaskResult, TaskStatistics,
    TaskStatus, TaskUpdate,
)
from todo_chat.security import get_current_user
from todo_chat.task_service import create_task, owned_task

router = APIRouter(prefix="/tasks", tags=["tasks"])
DatabaseSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TaskId = Annotated[int, Path(ge=1, le=2**63 - 1)]


@router.get("", response_model=TaskList)
def list_tasks(
    session: DatabaseSession,
    user: CurrentUser,
    status: TaskStatus | None = None,
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
    sort: Literal["newest", "oldest"] = "newest",
):
    query = select(Task).where(Task.owner_user_id == user.id)
    if status is not None:
        query = query.where(Task.status == status)
    order = (Task.created_at.desc(), Task.id.desc()) if sort == "newest" else (Task.created_at.asc(), Task.id.asc())
    query = query.order_by(*order)
    if limit is not None:
        query = query.limit(limit)
    return {"tasks": session.scalars(query).all()}


@router.post("", response_model=TaskResult, status_code=201)
def add_task(payload: TaskCreate, session: DatabaseSession, user: CurrentUser):
    return {"task": create_task(session, user.id, payload)}


# Register the static route before /{task_id}.
@router.get("/stats", response_model=TaskStatistics)
def statistics(session: DatabaseSession, user: CurrentUser):
    counts = dict(session.execute(
        select(Task.status, func.count(Task.id))
        .where(Task.owner_user_id == user.id).group_by(Task.status)
    ).all())
    pending = counts.get(TaskStatus.pending, 0)
    completed = counts.get(TaskStatus.completed, 0)
    return {"total": pending + completed, "pending": pending, "completed": completed}


@router.get("/{task_id}", response_model=TaskResult)
def get_task(task_id: TaskId, session: DatabaseSession, user: CurrentUser):
    return {"task": owned_task(session, user.id, task_id)}


@router.patch("/{task_id}", response_model=TaskResult)
def update_task(task_id: TaskId, payload: TaskUpdate, session: DatabaseSession, user: CurrentUser):
    task = owned_task(session, user.id, task_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    session.commit()
    session.refresh(task)
    return {"task": task}


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: TaskId, session: DatabaseSession, user: CurrentUser):
    task = owned_task(session, user.id, task_id)
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}
