from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str
    app_port: int
    allow_host: str
    allow_port: int
    current_port: int

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_pass: str
    postgres_db: str

    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
