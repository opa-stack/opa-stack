from fastapi import APIRouter, Depends

from opa.core.plugin import BasePlugin, get_component
from opa.plugins.driver_redis import Walrus

router = APIRouter()


@router.get("/counter-async")
async def counter_async(aioredis=Depends(get_component('aioredis')), key=None):
    counter = await aioredis.instance.incr(key or 'incr-async')
    return f'Counter is {counter}'


@router.get("/counter-sync")
def counter_sync(walrus: Walrus = Depends(get_component('walrus')), key=None):
    counter = walrus.instance.incr(key or 'incr-sync')
    return f'Counter is {counter}'


@router.get("/bloom")
def check_bloom_filter(string: str, walrus=Depends(get_component('walrus'))):
    bf = walrus.instance.bloom_filter('bf')
    return string in bf


@router.post("/bloom")
def add_bloom_filter(string: str, walrus=Depends(get_component('walrus'))):
    # Waiting for https://github.com/tiangolo/fastapi/issues/1018 to have plain/text input
    # Possible now, but not with generation of the openapi spec..
    bf = walrus.instance.bloom_filter('bf')
    for i in string.split(' '):
        bf.add(i)

    return f'Added entries'


class Plugin(BasePlugin):
    def setup(self, app):
        app.include_router(router)
