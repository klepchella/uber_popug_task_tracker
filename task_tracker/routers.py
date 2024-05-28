from datetime import timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import PositiveInt
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK


api_router = APIRouter()
