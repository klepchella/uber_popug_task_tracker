from enum import Enum
from uuid import UUID

from pydantic import BaseModel

TOKEN_TYPE = "bearer"


class RoleEnum(Enum):
    ADMIN = 1
    MANAGER = 2
    CLIENT = 3


class User(BaseModel):
    id: int
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    public_id: UUID
    role: int


class Token(BaseModel):
    user_id: int
    token: str
    token_type: str
