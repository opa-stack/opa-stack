from fastapi import APIRouter, Depends

from opa.utils.redis import get_aioredis, get_walrus

router = APIRouter()


@router.get("/counter")
async def return_count(airoredis=Depends(get_aioredis)):
    await airoredis.incr('a')
    counter = await airoredis.get('a')
    return f'Counter is {counter}'


def setup(app, **kwargs):
    app.include_router(router)
