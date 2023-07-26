from db.database import engine


async def check_postgres_connection():
    try:
        async with engine.connect():
            return True

    except Exception as error:
        return error
