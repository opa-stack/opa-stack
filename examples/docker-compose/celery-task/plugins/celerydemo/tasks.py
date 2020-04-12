from time import sleep

from celery import current_task

from opa import get_instance

celery = get_instance('celery')


@celery.task
def counter(count: int) -> str:
    walrus = get_instance('walrus')
    for i in range(count):
        sleep(1)
        status = walrus.incr('celery')
        current_task.update_state(
            state='PROGRESS',
            meta={'process_percent': i * (100 / count), 'current_inc': status},
        )

    return f'incremented to {status}'


@celery.task
def divider(num1, num2) -> str:
    sleep(4)

    result = num1 / num2
    return f'The result was {result}'
