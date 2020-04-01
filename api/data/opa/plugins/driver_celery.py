import logging

from opa.core.plugin import Driver, Hook, Setup, HookDefinition
from opa.utils import host_exists


class hookname(HookDefinition):
    ...


class ahook(Hook):
    name = 'hookname'

    def run(self):
        print('running hook')


class Celery(Driver):
    name = 'celery'

    def connect(self, opts):
        print('connecting celery')
        # if not host_exists(opts.URL, 'database-url'):
        #     return None

        logging.info(f"Connectiong to celery using {opts}")

        self.instance = None

    def disconnect(self):
        pass


from fastapi import FastAPI, BackgroundTasks

from opa.utils import celery_app

from fastapi import APIRouter
from opa.core.plugin import BasePlugin

router = APIRouter()


@router.get("/testa")
async def root():
    return {"message": "test"}


from fastapi import APIRouter, Depends

from opa.core.plugin import BasePlugin, get_component

from opa.plugins.driver_redis import Walrus

router = APIRouter()


@router.get("/counter-async")
async def counter_async(aioredis=Depends(get_component('aioredis')), key=None):
    counter = await aioredis.instance.incr(key or 'incr-async')
    return f'Counter is {counter}'


@router.get("/counter-sync")
def counter_sync(walrus=Depends(get_component('walrus')), key=None):
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


class Test(Setup):
    def __init__(self, app):
        print('test-setup')
        app.include_router(router)
