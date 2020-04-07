from time import sleep

from celery import current_task

from opa import get_instance

celery = get_instance('celery')

@celery.task
def test_celery(word: str) -> str:
    for i in range(1, 4):
        sleep(1)
        current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': i*10})

    get_instance('walrus').incr('celery')
    return f"test task return {word}...."