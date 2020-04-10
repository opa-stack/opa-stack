from opa import get_router, Hook, get_instance


class celery_config(Hook):
    name = 'driver.celery.setup'

    def run(self, celery_app):
        celery_app.conf.task_routes = {
            'celerydemo.tasks.counter': 'counter',
            'celerydemo.tasks.divider': 'math',
        }
        celery_app.conf.update(task_track_started=True)
        return celery_app


router = get_router()


@router.get('/inc')
def counter(num1: int, num2: int):
    from celerydemo.tasks import counter

    walrus = get_instance('walrus')
    current_count = str(walrus.get('celery'))
    counter.delay()
    return {'status': 'queued', 'current_count': current_count}


@router.get('/div/{num1}/{num2}')
def divider(num1: int, num2: int):
    from celerydemo.tasks import divider

    divider.delay(num1, num2)
    return {'status': 'queued'}
