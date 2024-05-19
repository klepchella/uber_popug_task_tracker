import datetime

from sqlalchemy import Table, Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy import UUID

from auth.database import metadata

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, default="Unknown user", unique=True),
    Column("password", String, nullable=False),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("email", String, nullable=True),
    Column("public_id", UUID, nullable=False),
    Column("role", Integer, nullable=False),
)

oauth_token = Table(
    "oauth_token",
    metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("token", String, nullable=False),
    Column("token_type", String, nullable=False),
)
