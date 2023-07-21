from .database import engine


async def check_postgres_connection():
    try:
        async with engine.connect() as conn:
            return True

    except Exception as error:
        return error
