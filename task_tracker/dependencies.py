from typing import AsyncIterator

from aiopg.sa import SAConnection
from fastapi import Depends, Request
from sqlalchemy.orm import Session

import settings
from integrations import AuthAPI
from task_tracker.database import session as db_session
from task_tracker.repository import UserRepository, TaskRepository


async def get_session() -> AsyncIterator[SAConnection]:
    db = db_session()
    try:
        yield db
    finally:
        db.close()


async def get_user_repository(
    request: Request, session: Session = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)


async def get_task_repository(
    request: Request, session: Session = Depends(get_session)
) -> TaskRepository:
    return TaskRepository(session)


async def get_auth_api(
    request: Request,
):
    return AuthAPI(
        auth_url=settings.settings_.auth_host,
    )
