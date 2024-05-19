import abc
import uuid
from datetime import timedelta, datetime, timezone
from typing import TypeVar, Sequence, Generic, Annotated

from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from sqlalchemy import Table, Select, select, insert, delete, update
from sqlalchemy.orm import Session
from starlette import status

from auth.security import (
    get_password_hash,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
    TokenData,
    verify_password,
)
from auth.tables import user, oauth_token
from auth.types import User, Token, TOKEN_TYPE

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT], abc.ABC):
    @property
    @abc.abstractmethod
    def model_cls(self) -> type[ModelT]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def table(self) -> Table:
        raise NotImplementedError

    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_from_query(self, query: Select) -> Sequence[ModelT]:
        model_cls = self.model_cls
        with self._session.execute(query) as rows:
            result = rows.fetchall()
        return tuple(model_cls(**row._mapping) for row in result)


class UserRepository(BaseRepository):
    table = user
    model_cls = User

    def find_user_by_user_name(self, username: str) -> User | None:
        query = (
            select(
                self.table.c.id,
                self.table.c.password,
                self.table.c.username,
                self.table.c.first_name,
                self.table.c.last_name,
                self.table.c.email,
                self.table.c.public_id,
                self.table.c.role,
            )
            .select_from(self.table)
            .where(self.table.c.username == username)
        )
        result = self._get_from_query(query)
        if len(result) == 0:
            return None
        return result[0]

    def create_user(
        self,
        username: str,
        password: str,
        role: int,
        first_name: str,
        last_name: str,
        email: str,
    ) -> None:
        password_hash = get_password_hash(password)
        query = insert(self.table).values(
            username=username,
            password=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            public_id=uuid.uuid4(),
        )
        # with self._session.begin():
        self._session.execute(query)
        self._session.commit()

    def update_user(
        self,
        user_id: int,
        username: str | None = None,
        role: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> None:
        query = (
            update(self.table)
            .where(self.table.c.id == user_id)
            .values(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
            )
        )
        # with self._session.begin():
        self._session.execute(query)
        self._session.commit()

    def delete_user(self, user_id: int) -> None:
        query = delete(self.table).where(self.table.c.id == user_id)
        # with self._session.begin():
        self._session.execute(query)
        self._session.commit()


class AuthRepository(BaseRepository):
    table = oauth_token
    model_cls = Token

    def create_token(
        self, user_id: int, data: dict, expires_delta: timedelta | None = None
    ) -> Token | None:
        token = create_access_token(data, expires_delta)
        query = insert(self.table).values(
            user_id=user_id,
            token=token,
            token_type=TOKEN_TYPE,
        )
        self._session.execute(query)
        self._session.commit()
        return Token(token=token, token_type=TOKEN_TYPE, user_id=user_id)

    def is_verify_token(self, user_id: int, token: str) -> bool:
        query = (
            select(
                self.table.c.user_id,
                self.table.c.token,
                self.table.c.token_type,
            )
            .select_from(self.table)
            .where(self.table.c.user_id == user_id, self.table.c.token == token)
        )
        result = self._get_from_query(query)
        if len(result) == 0:
            return False
        return True


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: UserRepository,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = user_repository.find_user_by_user_name(username)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(user_repository: UserRepository, username: str, password: str):
    user = user_repository.find_user_by_user_name(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
