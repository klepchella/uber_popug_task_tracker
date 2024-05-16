from sqlalchemy import Table, Column, Integer, String
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
