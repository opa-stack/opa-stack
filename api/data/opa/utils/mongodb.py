from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from opa import config, log


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def connect_to_mongo():
    log.info("Connecting to mongodb database..")
    db.client = AsyncIOMotorClient(
        config.OPTIONAL_COMPONENTS.MONGODB.URL,
        socketTimeoutMS=1000,
        connectTimeoutMS=1000,
        serverSelectionTimeoutMS=1000,
    )

    # This throws an exception if not connected
    info = await db.client.server_info()
    log.debug(info)


async def close_mongo_connection():
    log.info("Closing mongodb connection")
    db.client.close()


async def get_database(name=None) -> AsyncIOMotorDatabase:
    return db.client[name or 'opa']
