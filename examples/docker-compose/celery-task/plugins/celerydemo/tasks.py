from time import sleep

from celery import current_task

from opa import get_instance

celery = get_instance('celery')


@celery.task
def counter() -> str:

    for i in range(4):
        sleep(1)
        current_task.update_state(state='PROGRESS', meta={'process_percent': i * 20})

    status = get_instance('walrus').incr('celery')
    return f'incremented to {status}'


@celery.task
def divider(num1, num2) -> str:
    sleep(4)

    result = num1 / num2
    return f'The result was {result}'
