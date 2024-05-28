from pydantic_settings import BaseSettings


class WebAppSettings(BaseSettings):
    port: int
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_db: str
    kafka_host: str

    class Config:
        env_file = "local_auth.env"


settings_ = WebAppSettings()
