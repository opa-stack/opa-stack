from time import sleep
from secrets import token_urlsafe

from fastapi import BackgroundTasks, APIRouter

from opa import get_router, get_instance

router = get_router()


def queuer(text: str):
    walrus = get_instance('walrus')
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
async def runone_get():
    walrus = get_instance('walrus')
    return {"current_task": walrus.get('runone')}
