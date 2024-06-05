from sqlalchemy import Table, Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy import UUID

from task_tracker.database import metadata


account = Table(
    "account",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False, default="Unknown account", unique=True),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
    Column("email", String, nullable=True),
    Column("user_public_id", UUID, nullable=False, unique=True),
    Column("role", Integer, nullable=False),
)

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("task_public_id", UUID, unique=True, nullable=False),
    Column(
        "user_id",
        ForeignKey("account.user_public_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("cost", DECIMAL, nullable=False),
    Column("status", Integer),
    Column("description", String),
)
payment = Table(
    "payment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "task_public_id",
        ForeignKey("task.task_public_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id",
        ForeignKey("account.user_public_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("summa", DECIMAL),
)
