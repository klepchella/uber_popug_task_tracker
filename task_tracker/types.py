import uuid
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(Enum):
    admin = 1
    manager = 2
    client = 3


class TaskStatusEnum(Enum):
    to_do = 1
    in_progress = 2
    done = 3
    failed = 4


class User(BaseModel):
    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    user_public_id: UUID
    role: int


class Task(BaseModel):
    id: int
    user_id: uuid.UUID
    task_public_id: uuid.UUID
    cost: Decimal
    status: int
    description: str

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


class Payment(BaseModel):
    id: int
    task_id: uuid.UUID
    user_id: uuid.UUID
    summa: Decimal


class Dashboard(BaseModel):
    task_public_id: uuid.UUID
    username: str
    cost: Decimal
    description: str
    status: TaskStatusEnum
    email: str
