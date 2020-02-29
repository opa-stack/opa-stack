from starlette.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

from .core import plugin, config

from .db.mongodb_utils import close_mongo_connection, connect_to_mongo

app = FastAPI(
    title=config.PROJECT_NAME, description=config.PROJECT_DESCRIPTION, version="0.0.2"
)

plugin.initialize(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*",],
    allow_headers=["*",],
)


app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
