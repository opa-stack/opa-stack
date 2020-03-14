from fastapi import APIRouter, Depends

from opa.utils.redis import get_aioredis, get_walrus

router = APIRouter()


@router.get("/counter-async")
async def counter_async(airoredis=Depends(get_aioredis), key=None):
    key = key or 'incr-async'
    counter = await airoredis.incr(key)
    return f'Counter is {counter}'


@router.get("/counter-sync")
def counter_sync(walrus=Depends(get_walrus), key=None):
    key = key or 'incr-sync'
    counter = walrus.incr(key)
    return f'Counter is {counter}'


@router.get("/bloom")
def check_bloom_filter(string: str, walrus=Depends(get_walrus)):
    bf = walrus.bloom_filter('bf')
    return string in bf


@router.post("/bloom")
def add_bloom_filter(string: str, walrus=Depends(get_walrus)):
    # Waiting for https://github.com/tiangolo/fastapi/issues/1018 to have plain/text input
    # Possible now, but not with generation of the openapi spec..
    bf = walrus.bloom_filter('bf')
    for i in string.split(' '):
        bf.add(i)

    return f'Added entries'


def setup(app, **kwargs):
    app.include_router(router)
