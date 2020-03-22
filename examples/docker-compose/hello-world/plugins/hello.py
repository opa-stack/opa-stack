from fastapi import APIRouter
from opa.core.plugin import BasePlugin

router = APIRouter()


@router.get("/hello")
def return_string():
    return 'Hello to you'


class Plugin(BasePlugin):
    def setup(self, app):
        app.include_router(router)
