from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from todo_chat.database import get_session
from todo_chat.models import User
from todo_chat.schema import BotMessage, BotReply, TaskCreate
from todo_chat.security import get_current_user
from todo_chat.task_service import create_task

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=BotReply)
def send_message(
    payload: BotMessage,
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
):
    task = create_task(session, user.id, TaskCreate(title=payload.text))
    return {"reply": f"Added task: {task.title}", "task": task}
