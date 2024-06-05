from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy import UUID

from auth.database import metadata

account = Table(
    "account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, default="Unknown account", unique=True),
    Column("password", String, nullable=False),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("email", String, nullable=True),
    Column("user_public_id", UUID, nullable=False, unique=True),
    Column("role", ForeignKey("role.id"), nullable=False),
)

oauth_token = Table(
    "auth",
    metadata,
    Column("user_id", ForeignKey("account.id", ondelete="CASCADE"), primary_key=True),
    Column("token", String, nullable=False),
    Column("token_type", String, nullable=False),
)

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)
