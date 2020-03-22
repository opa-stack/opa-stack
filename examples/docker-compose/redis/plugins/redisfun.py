from fastapi import APIRouter, Depends

from opa.utils.redis import get_aioredis, get_walrus
from opa.core.plugin import BasePlugin, get_component, get_redis, get_plugin_manager

router = APIRouter()


@router.get("/counter-async")
async def counter_async(aioredis=Depends(get_component('aioredis')), key=None):
    key = key or 'incr-async'
    counter = await aioredis.incr(key)
    return f'Counter is {counter}'


@router.get("/counter-sync")
def counter_sync(walrus=Depends(get_component('walrus')), key=None):
    key = key or 'incr-sync'
    counter = walrus.incr(key)
    return f'Counter is {counter}'


@router.get("/bloom")
def check_bloom_filter(string: str, walrus=Depends(get_component('walrus'))):
    bf = walrus.bloom_filter('bf')
    return string in bf


@router.post("/bloom")
def add_bloom_filter(string: str, walrus=Depends(get_component('walrus'))):
    # Waiting for https://github.com/tiangolo/fastapi/issues/1018 to have plain/text input
    # Possible now, but not with generation of the openapi spec..
    bf = walrus.bloom_filter('bf')
    for i in string.split(' '):
        bf.add(i)

    return f'Added entries'


class Plugin(BasePlugin):
    def setup(self, app):
        app.include_router(router)
