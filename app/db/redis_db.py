# import asyncio
# from redis import asyncio as aioredis
#
# REDIS_URL = "redis://:myredispassword@redis"
#
# async def get_redis():
#     redis = await aioredis.create_redis_pool(REDIS_URL)
#     yield redis
#     redis.close()
#     await redis.wait_closed()