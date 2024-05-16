from pydantic_settings import BaseSettings


class WebAppSettings(BaseSettings):
    port: int = 8000
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str

    class Config:
        env_file = "local.env"


settings_ = WebAppSettings()
