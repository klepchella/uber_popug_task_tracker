import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from pydantic import PositiveInt
from starlette.requests import Request
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from task_tracker.dependencies import get_task_repository, get_auth_api, get_user_repository
from task_tracker.integrations import AuthAPI
from task_tracker.repository import TaskRepository, UserRepository
from task_tracker.types import Dashboard

api_router = APIRouter()


@api_router.post("/task/create")
def create_task(
    request: Request,
    auth_api: Annotated[AuthAPI, Depends(get_auth_api)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    task_repository: Annotated[TaskRepository, Depends(get_task_repository)],
    token: str,
    public_user_id: uuid.UUID,
    cost: Decimal,
    description: str,
) -> PositiveInt:
    if not auth_api.check_role(public_user_id=public_user_id, token=token):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )
    # todo: добавить валидацию при сохрании, сейчас считаем, что у нас всегда добавляется таска, которой нет в БД
    task_repository.create_task(cost=cost, description=description)
    return HTTP_200_OK


@api_router.post("/task/check")
def assign_task(
    request: Request,
    auth_api: Annotated[AuthAPI, Depends(get_auth_api)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token: str,
    public_user_id: uuid.UUID,
) -> PositiveInt:
    # проверяем совпадение токена и юзер_айди и роль юзера, либо он админ, либо менеджер
    if not auth_api.check_role(
        public_user_id=public_user_id, token=token
    ) or not user_repository.check_role(public_user_id=public_user_id):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )
    return HTTP_200_OK


@api_router.post("/task/reassign")
def assign_task(
    request: Request,
    auth_api: Annotated[AuthAPI, Depends(get_auth_api)],
    task_repository: Annotated[TaskRepository, Depends(get_task_repository)],
    token: str,
    public_user_id: uuid.UUID,
) -> PositiveInt:
    # проверяем роль юзера, либо он админ, либо менеджер
    if not auth_api.check_role(public_user_id=public_user_id, token=token):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )

    # если всё ок, то ассайним задачи
    task_repository.reassign_task()
    return HTTP_200_OK


@api_router.post("/task/dashboard")
def assign_task(
    request: Request,
    task_repository: Annotated[TaskRepository, Depends(get_task_repository)],
) -> list[Dashboard]:
    # если всё ок, то ассайним задачи
    return task_repository.dashboard()
