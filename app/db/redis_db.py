import asyncio_redis
from config import settings


async def check_redis_connection():
    try:
        connection = await asyncio_redis.Connection.create(host=settings.redis_host, port=settings.redis_port)
        response = await connection.ping()
        connection.close()
        return response

    except Exception as error:
        return error
