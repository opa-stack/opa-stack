import sys

from starlette.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

from opa import config, init_configuration
from opa.core import plugin

app: FastAPI


def plugin_setup():
    """
    This function is called after app is available (via on_startup)
    """
    plugin.setup(app)


def start_app():
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
        on_startup=[plugin.startup, plugin_setup],
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


if 'uvicorn' in sys.argv[0]:
    start_app()
