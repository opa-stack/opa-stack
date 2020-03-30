from fastapi import APIRouter
from opa.core.plugin import Setup

router = APIRouter()


@router.get("/hello")
def return_string():
    return 'Hello to you'


class Hello(Setup):
    def __init__(self, app):
        app.include_router(router)
