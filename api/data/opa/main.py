import sys

from typing import Any

from starlette.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

from opa import config, init_configuration, state
from opa.core import plugin

app: FastAPI

async def plugin_startup():
    """
    This function is called after app is available (via on_startup)
    """
    await plugin.startup(app)


def start_api():
    global app
    init_configuration()

    app = FastAPI(
        title=config.PROJECT_NAME,
        description=config.PROJECT_DESCRIPTION,
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        openapi_url=config.OPENAPI_URL,
        version=config.PROJECT_VERSION,
        openapi_prefix=config.OPENAPI_PREFIX,
        debug=config.DEBUG,
        on_startup=[plugin_startup],
        on_shutdown=[plugin.shutdown],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOW_ORIGINS,
        allow_credentials=config.ALLOW_CREDENTIALS,
        allow_methods=config.ALLOW_METHODS,
        allow_headers=config.ALLOW_HEADERS,
    )

    return app

def start_worker():
    global celery
    init_configuration()
    plugin.startup_worker()

    # We must export main.celery for the worker to be happy
    celery = plugin.plugin_manager.optional_components['celery'].instance

if 'uvicorn' in sys.argv[0]:
    state['runner'] = 'uvicorn'
    start_api()
elif 'celery' in sys.argv[0]:
    state['runner'] = 'celery'
    start_worker()