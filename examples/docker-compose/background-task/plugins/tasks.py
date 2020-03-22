from time import sleep
from secrets import token_urlsafe

from fastapi import BackgroundTasks, APIRouter, Depends

from opa.utils.redis import get_walrus
from opa.core.plugin import BasePlugin

router = APIRouter()


def queuer(text: str):
    walrus = get_walrus()  # You can't use dependency injection when inside a task
    lock = walrus.lock('runone')

    with lock:
        walrus.set('runone', text)
        sleep(4)
        walrus.delete('runone')


@router.post("/runone")
async def runone_post(background_tasks: BackgroundTasks):
    random_str = token_urlsafe(5)
    background_tasks.add_task(queuer, random_str)
    return {"message": f"Triggered background task: {random_str}"}


@router.get("/runone")
async def runone_get(walrus=Depends(get_walrus)):
    return {"current_task": walrus.get('runone')}


class Plugin(BasePlugin):
    def setup(self, app):
        app.include_router(router)
