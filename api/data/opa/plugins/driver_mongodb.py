import logging

from motor.motor_asyncio import AsyncIOMotorClient

from opa.core.plugin import Driver
from opa.utils import host_exists


class MongodbMotorAsync(Driver):
    name = 'mongodb-async-motor'
    instance: AsyncIOMotorClient = None

    async def connect(self, opts):
        if not host_exists(opts.URL, 'database-url'):
            return None

        logging.info("Connecting to mongodb database..")
        self.instance = AsyncIOMotorClient(
            opts.URL,
            socketTimeoutMS=1000,
            connectTimeoutMS=1000,
            serverSelectionTimeoutMS=1000,
        )

        # This throws an exception if not connected
        info = await self.instance.server_info()
        logging.debug(info)

    async def disconnect(self):
        logging.info("Closing mongodb connection")
        self.instance.close()

    def get(self):
        return self.instance[name or 'opa']
