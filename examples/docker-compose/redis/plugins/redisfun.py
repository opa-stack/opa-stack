from fastapi import Request
from opa import get_instance, get_router

router = get_router()


@router.get("/counter-async")
async def counter_async(key=None):
    counter = await get_instance('aioredis').incr(key or 'incr-async')
    return f'Counter is {counter}'


@router.get("/counter-sync")
def counter_sync(key=None):
    counter = get_instance('walrus').incr(key or 'incr-sync')
    return f'Counter is {counter}'


@router.get("/bloom")
def check_bloom_filter(string: str):
    walrus = get_instance('walrus')
    bf = walrus.bloom_filter('bf')
    return string in bf


@router.post("/bloom")
async def add_bloom_filter(request: Request, string: str = None):
    # Waiting for https://github.com/tiangolo/fastapi/issues/1018 to have plain/text input
    # Possible now, but not with generation of the openapi spec..
    walrus = get_instance('walrus')
    bf = walrus.bloom_filter('bf')

    if string is None:
        async for chunk in request.stream():
            for i in chunk.split():
                bf.add(i)
    else:
        for i in string.split():
            bf.add(i)

    return 'Added entries'
