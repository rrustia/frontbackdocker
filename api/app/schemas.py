from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# I use literal values so invalid statuses fail fast during request validation.
TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    due_date: date | None = None


class TaskUpdate(BaseModel):
    # I keep fields optional so PATCH requests can send partial updates.
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=200)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthUserOut(BaseModel):
    username: str
