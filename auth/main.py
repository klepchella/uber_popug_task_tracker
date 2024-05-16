import uvicorn
from fastapi import FastAPI

from auth.routers import api_router
from auth.settings import settings_

SERVICE_NAME = "auth"

app = FastAPI(
    title=SERVICE_NAME,
)
app.include_router(api_router, prefix="/auth")


if __name__ == "__main__":
    uvicorn.run(app, port=settings_.port, log_config=None)
