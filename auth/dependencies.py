from fastapi import Depends, Request
from sqlalchemy.orm import Session

from auth.database import session as db_session
from auth.repository import UserRepository


def get_session():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(
    request: Request, session: Session = Depends(get_session)
) -> UserRepository:
    return UserRepository(session)
