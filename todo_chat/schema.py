from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class UserBase(BaseModel):
    name: Name
    email: EmailStr


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class CurrentUserResponse(BaseModel):
    user: UserResponse


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"


class TaskBase(BaseModel):
    title: Title
    description: str | None = None


class TaskCreate(TaskBase):
    model_config = ConfigDict(extra="forbid")


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title | None = None
    description: str | None = None
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for field in ("title", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    status: TaskStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    owner_user_id: int = Field(serialization_alias="ownerUserId")


class ChatState(str, Enum):
    idle = "idle"
    waiting_description = "waiting_description"
    completed = "completed"


class ChatSessionBase(BaseModel):
    state: ChatState
    last_message: str | None = None


class ChatSessionResponse(ChatSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
