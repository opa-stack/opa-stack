import logging
import aioredis as aioredislib
import walrus as walruslib


class Redis:
    aioredis = None
    walrud = None


redis = Redis()


async def connect_to_aioredis():
    logging.info("Connectiong to redis using aioredis")
    redis.aioredis = await aioredislib.create_redis_pool('redis://redis')


async def close_aioredis_connection():
    redis.aioredis.close()
    await redis.aioredis.wait_closed()


async def get_aioredis():
    return redis.aioredis


async def connect_to_walrus():
    logging.info("Connectiong to redis using walrus")
    redis.walrus = walruslib.Database.from_url('redis://redis')

    # Raises exception if not able to connect
    redis.walrus.client_id()


def get_walrus():
    return redis.walrus
