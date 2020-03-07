from starlette.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

from .core import plugin, config

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
