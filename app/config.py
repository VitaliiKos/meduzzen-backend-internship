from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(filename=".env", usecwd=True), env_file_encoding='utf-8',
                                      extra='allow')

    app_host: str
    app_port: int
    allow_host: str
    allow_port: int
    current_port: int

    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_user: str = 'tamtik'
    postgres_pass: str = 'root'
    postgres_db: str = 'tamtik'
    database_url: str = f'postgresql+asyncpg://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}'

    redis_host: str
    redis_port: int

    celery_port: int

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int

    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str

    celery_broker_url: str
    celery_result_backend: str

    owner: str


settings = Settings()
