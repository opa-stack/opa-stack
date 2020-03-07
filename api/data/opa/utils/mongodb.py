import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from opa.core import config


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database(name=None) -> AsyncIOMotorDatabase:
    return db.client[name or 'opa']


async def connect_to_mongo():
    logging.info("Connecting to mongodb database..")
    db.client = AsyncIOMotorClient(
        config.OPTIONAL_COMPONENTS.MONGODB.URL,
        socketTimeoutMS=1000,
        connectTimeoutMS=1000,
        serverSelectionTimeoutMS=1000,
    )

    # This throws an exception if not connected
    logging.info(await db.client.server_info())


async def close_mongo_connection():
    logging.info("Closing mongodb connection")
    db.client.close()
