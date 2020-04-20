import aioredis as aioredislib
import walrus as walruslib

from opa import config, log


class Redis:
    aioredis = None
    walrus = None


redis = Redis()


async def connect_to_aioredis():
    log.info("Connectiong to redis using aioredis")
    redis.aioredis = await aioredislib.create_redis_pool(
        config.OPTIONAL_COMPONENTS.REDIS.URL
    )


async def close_aioredis_connection():
    redis.aioredis.close()
    await redis.aioredis.wait_closed()


async def get_aioredis():
    return redis.aioredis


async def connect_to_walrus():
    log.info("Connectiong to redis using walrus")
    redis.walrus = walruslib.Database.from_url(config.OPTIONAL_COMPONENTS.REDIS.URL)

    # Raises exception if not able to connect
    redis.walrus.client_id()


def get_walrus():
    return redis.walrus
