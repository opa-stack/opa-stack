from fastapi import FastAPI, BackgroundTasks

from fastapi import APIRouter
from opa.core.plugin import BasePlugin

router = APIRouter()

"""
@store.app.task(acks_late=True)
def test_celery(word: str) -> str:
    from time import sleep
    from celery import current_task

    for i in range(1, 11):
        sleep(1)
        current_task.update_state(
            state='PROGRESS', meta={'process_percent': i * 10}
        )
    return f"test task return {word}"
"""


def celery_on_message(body):
    print(body)


def background_on_message(task):
    print(task.get(on_message=celery_on_message, propagate=False))


@router.get("/{word}")
async def root(word: str, background_task: BackgroundTasks):
    # task = celery_app.send_task("opa.utils.celery_app.test_celery", args=[word])
    # print(task)
    # background_task.add_task(background_on_message, task)
    return {"message": "Word received"}
