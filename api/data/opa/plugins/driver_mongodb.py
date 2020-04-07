import logging

from motor.motor_asyncio import AsyncIOMotorClient

from opa import Driver
from opa.utils import host_exists


class MongodbMotorAsync(Driver):
    name = 'mongodb-async-motor'
    instance: AsyncIOMotorClient = None

    async def connect(self):
        if not host_exists(self.opts.URL, 'database-url'):
            return False

        self.instance = AsyncIOMotorClient(
            self.opts.URL,
            socketTimeoutMS=1000,
            connectTimeoutMS=1000,
            serverSelectionTimeoutMS=1000,
        )

        # This throws an exception if not connected
        info = await self.instance.server_info()
        logging.debug(info)

    async def disconnect(self):
        self.instance.close()

    def get_instance(self):
        return self.instance[name or 'opa']
