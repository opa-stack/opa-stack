from opa import get_router, Hook, get_instance, app


class celery_config(Hook):
    name = 'driver.celery.setup'

    def run(self, celery_app, task_candidates):
        celery_app.conf.task_routes = {"worker.celery_worker.test_celery": "test-queue"}
        celery_app.conf.update(task_track_started=True)
        celery_app.autodiscover_tasks(task_candidates)
        return celery_app


router = get_router()


@router.get("/add/{num1}/{num2}")
async def root(num1: int, num2: int):
    from celerydemo.tasks import test_celery

    celery = get_instance('celery')
    walrus = get_instance('walrus')
    test_celery.delay('abc')
    count = str(walrus.get('celery'))
    return {"message": "Word received", 'count': count}
