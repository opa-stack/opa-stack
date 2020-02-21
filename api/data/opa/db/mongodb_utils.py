import logging

from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import MONGODB_URL
from .mongodb import db


async def connect_to_mongo():
    logging.info("Connecting to database..")
    db.client = AsyncIOMotorClient(str(MONGODB_URL), connectTimeoutMS=5000)
    logging.info("Connection to database succeeded")


async def close_mongo_connection():
    logging.info("Closing database connection")
    db.client.close()
    logging.info("Database connection closed")
