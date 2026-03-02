from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum



class UserBase(BaseModel):
    username: str
    email: EmailStr
class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TaskBase(BaseModel):
    title:str
    description: str | None=None

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    status: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "strict": True
    }

class ChatState(str, Enum):
    idle = "idle"
    waiting_description = "waiting_description"
    completed = "completed"

class ChatSessionBase(BaseModel):
    state:ChatState
    last_message: Optional[str] = None

class ChatSessionResponse(ChatSessionBase):
    id: int
    created_at: datetime
    model_config = {
        "from_attributes" : True
    }




