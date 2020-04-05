from time import sleep

from celery import current_task

from opa.core.plugin import plugin_manager

celery = plugin_manager.optional_components['celery'].instance

@celery.task
def test_celery(word: str) -> str:
    for i in range(1, 4):
        sleep(1)
        current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': i*10})
    plugin_manager.optional_components['walrus'].instance.incr('celery')
    return f"test task return {word}"