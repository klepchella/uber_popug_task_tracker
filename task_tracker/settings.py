from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class WebAppSettings(BaseSettings):
    port: int = 8001
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str
    kafka_host: str
    auth_host: AnyHttpUrl

    class Config:
        env_file = "local_task_tracker.env"


settings_ = WebAppSettings()
