from datetime import timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import PositiveInt
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK

from auth.dependencies import get_user_repository, get_auth_repository
from auth.repository import (
    UserRepository,
    authenticate_user,
    AuthRepository,
)
from auth.security import (
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from auth.types import RoleEnum

api_router = APIRouter()


@api_router.post("/login")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_repository: Annotated[AuthRepository, Depends(get_auth_repository)],
) -> Token:
    user = authenticate_user(user_repository, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token_repository.create_token(
        user_id=user.id, data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token.token, token_type=access_token.token_type)


@api_router.post("/create")
def create_user(
    request: Request,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: int = RoleEnum.CLIENT,
) -> PositiveInt:
    # todo: добавить валидацию при сохрании, сейчас считаем, что у нас всегда добавляется юзер, которого нет в БД
    user_repository.create_user(
        username=username,
        password=password,
        role=role,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    return HTTP_200_OK


@api_router.post("/update")
def update_user(
    request: Request,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
auth_repository: Annotated[AuthRepository, Depends(get_auth_repository)],
        token: str,
    user_id: int,
    username: str | None = None,
    role: int | None = RoleEnum.CLIENT,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> PositiveInt:
    if not auth_repository.is_verify_token(user_id=user_id, token=token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # todo: добавить валидацию на юзера
    user_repository.update_user(
        user_id=user_id,
        username=username,
        role=role,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    return HTTP_200_OK


@api_router.post("/delete")
def delete_user(
    request: Request,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repository: Annotated[AuthRepository, Depends(get_auth_repository)],
    token: str,
    user_id: int,
) -> PositiveInt:
    if not auth_repository.is_verify_token(user_id=user_id, token=token):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # todo: добавить валидацию
    user_repository.delete_user(
        user_id=user_id,
    )
    return HTTP_200_OK
