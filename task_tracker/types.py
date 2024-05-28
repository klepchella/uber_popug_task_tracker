from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    public_id: UUID
    role: int


class Task(BaseModel):
    id: int
    user_id: int
    cost: Decimal
    status: str
    description: str


class Payment(BaseModel):
    id: int
    task_id: int
    user_id: int
    summa: Decimal
