import asyncio_redis


async def check_redis_connection():
    try:
        connection = await asyncio_redis.Connection.create(host='redis', port=6379)
        response = await connection.ping()
        connection.close()
        return response == b'PONG'

    except Exception as error:
        return error
