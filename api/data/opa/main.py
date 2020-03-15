import sys

from starlette.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Header, HTTPException

from opa import config, init_configuration
from opa.core import plugin


def get_app():
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
    )

    plugin.init(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*",],
        allow_headers=["*",],
    )

    return app


if 'uvicorn' in sys.argv[0]:
    app = get_app()
