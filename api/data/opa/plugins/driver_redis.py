import logging
import aioredis as aioredislib
import walrus as walruslib

from opa.core.plugin import Driver
from opa.utils import host_exists


class Aioredis(Driver):
    name = 'redis-aioredis'

    async def connect(self, opts):
        if not host_exists(opts.URL, 'database-url'):
            return None
        logging.info(f"Connectiong to redis using aioredis and {opts}")

        self.instance = await aioredislib.create_redis_pool(opts.URL)

    async def disconnect(self):
        self.instance.close()
        self.instance.wait_closed()


class Walrus(Driver):
    name = 'redis-walrus'

    def connect(self, opts):
        if not host_exists(opts.URL, 'database-url'):
            return None

        logging.info(f"Connectiong to redis using walrus and {opts}")
        self.instance = walruslib.Database.from_url(opts.URL)

        # Returns exception if not ready
        self.instance.client_id()
        print('connect.intance', self.instance)
