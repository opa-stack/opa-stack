import logging
import aioredis as aioredislib
import walrus as walruslib

from opa import Driver
from opa.utils import host_exists


class Aioredis(Driver):
    name = 'redis-aioredis'

    async def connect(self):
        if not host_exists(self.opts.URL, 'database-url'):
            return False

        self.instance = await aioredislib.create_redis_pool(self.opts.URL)

    async def disconnect(self):
        self.instance.close()
        self.instance.wait_closed()


class Walrus(Driver):
    name = 'redis-walrus'

    def connect(self):
        if not host_exists(self.opts.URL, 'database-url'):
            return False

        self.instance = walruslib.Database.from_url(self.opts.URL)

    def validate(self):
        self.instance.client_id()
