import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from task_tracker.routers import api_router
from task_tracker.settings import settings_

SERVICE_NAME = "task_tracker"

app = FastAPI(
    title=SERVICE_NAME,
)
app.add_middleware(SessionMiddleware, secret_key="sdfjhsgfxzncvkjehsroiauwhtlkjznldknf")
app.include_router(api_router, prefix="/task_tracker")


if __name__ == "__main__":
    uvicorn.run(app, port=settings_.port, log_config=None)
