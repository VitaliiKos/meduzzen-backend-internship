from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str
    app_port: int

    class Config:
        env_file = "../.env"


@lru_cache()
def get_settings():
    return Settings()
