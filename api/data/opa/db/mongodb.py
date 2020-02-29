from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database(name=None) -> AsyncIOMotorDatabase:
    return db.client[name or 'opa']
