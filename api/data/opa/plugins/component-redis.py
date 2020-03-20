import logging
import aioredis as aioredislib
import walrus as walruslib

from opa.core.plugin import Component, BasePlugin


class Aioredis(Component):
    async def connect(self, opts):
        logging.info(f"Connectiong to redis using aioredis and {opts}")

        self.instance = await aioredislib.create_redis_pool(opts.URL)

    async def disconnect(self):
        self.instance.close()
        self.instance.wait_closed()


class Walrus(Component):
    def connect(self, opts):
        logging.info(f"Connectiong to redis using walrus and {opts}")
        self.instance = walruslib.Database.from_url(opts.URL)

        # Returns exception if not ready
        self.instance.client_id()


class Plugin(BasePlugin):
    def startup(self, register_driver):
        register_driver('redis-aioredis', Aioredis)
        register_driver('redis-walrus', Walrus)
