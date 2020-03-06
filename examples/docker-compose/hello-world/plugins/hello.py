from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
def return_string():
    return 'Hello to you'


def setup(app, **kwargs):
    app.include_router(router)
