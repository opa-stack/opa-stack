from fastapi import FastAPI, BackgroundTasks

from fastapi import APIRouter, Depends
from opa.core.plugin import Setup, Hook, get_component
from opa.plugins.driver_celery import CeleryDriver

class celery_config(Hook):
    name = 'driver.celery.setup'

    def run(self, celery_app, task_candidates):
        print('setup celery')
        print(task_candidates)
        celery_app.conf.task_routes = {"worker.celery_worker.test_celery": "test-queue"}
        celery_app.conf.update(task_track_started=True)
        celery_app.autodiscover_tasks(task_candidates)
        return celery_app


router = APIRouter()

@router.get("/add/{num1}/{num2}")
async def root(
    num1: int, num2: int, celery: CeleryDriver = Depends(get_component('celery')), walrus = Depends(get_component('walrus'))
):
    from celerydemo.tasks import test_celery
    test_celery.delay('abc')
    count = str(walrus.instance.get('celery'))
    return {"message": "Word received", 'count': count}


class Tasks(Setup):
    def __init__(self, app):
        app.include_router(router)
