from pydantic_settings import BaseSettings


class WebAppSettings(BaseSettings):
    port: int = 8001
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str
    kafka_host: str

    class Config:
        env_file = "local_task_tracker.env"


settings_ = WebAppSettings()
