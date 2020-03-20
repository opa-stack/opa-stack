import logging

from motor.motor_asyncio import AsyncIOMotorClient

from opa.core.plugin import Component, BasePlugin


class MongodbMotorAsync(Component):
    instance: AsyncIOMotorClient = None

    async def connect(self, opts):
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


class Plugin(BasePlugin):
    def startup(self, register_driver):
        register_driver('mongodb-async-motor', MongodbMotorAsync)
