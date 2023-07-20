from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str
    app_port: int
    allow_host: str
    allow_port: int
    current_port: int

    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
