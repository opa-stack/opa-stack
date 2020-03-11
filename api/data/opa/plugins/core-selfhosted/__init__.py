"""
Note that the folder named 'core-js-static' must be populated before this plugin works.

* Doesnt work yet..
* Need a lot more settings..
* https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs
"""

from fastapi import APIRouter
from starlette.staticfiles import StaticFiles

from opa import config


def setup(app, **kwargs):
    if config.SELF_HOSTED:
        app.mount(
            "/core-js-static",
            StaticFiles(directory="/data/opa/plugins/core-selfhosted/static"),
            name="core-js-static",
        )

        @app.get("/docs", include_in_schema=True)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app.title + " - Swagger UI 2",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="/core-js-static/swagger-ui-bundle.js",
                swagger_css_url="/core-js-static/swagger-ui.css",
            )

        @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_oauth2_redirect_html()

        @app.get("/redoc", include_in_schema=False)
        async def redoc_html():
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                redoc_js_url="/core-js-static/redoc.standalone.js",
            )
