import json
from fastapi import BackgroundTasks
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


def celery_on_message(body):
    walrus = get_instance('walrus')
    print(f'Got update from task: {body}')
    walrus.set('last_message', json.dumps(body))


def background_on_message(task):
    print(task.get(on_message=celery_on_message, propagate=False))


@router.get('/last_status')
def last_status():
    walrus = get_instance('walrus')
    return json.loads(walrus.get('last_message'))


@router.get('/status/{task_id}')
def status(task_id: str):
    celery = get_instance('celery')
    task = celery.AsyncResult(task_id)
    return {'state': task.state, 'result': task.result}


@router.get('/inc/{count}')
def counter(background_task: BackgroundTasks, count: int):
    from celerydemo.tasks import counter

    walrus = get_instance('walrus')
    current_count = str(walrus.get('celery'))
    task = counter.delay(count)
    background_task.add_task(background_on_message, task)
    return {'status': 'queued', 'current_count': current_count, 'task_id': str(task)}


@router.get('/div/{num1}/{num2}')
def divider(num1: int, num2: int):
    from celerydemo.tasks import divider

    divider.delay(num1, num2)
    return {'status': 'queued'}
