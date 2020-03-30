import logging
import datetime
import secrets

from time import sleep
from asyncio import sleep as async_sleep

from fastapi import APIRouter

from opa.core.plugin import Setup

router = APIRouter()

# Using tags helps separate your items from the also included demo-plugins
@router.get("/time", tags=["timekeeper"])
def get_time(format: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format)


@router.get("/month/{month}", tags=["timekeeper"])
def get_monthname(month: int):
    """
    Make sure you give me a valid month number, or I might crash...
    """
    return datetime.datetime.strptime(str(month), '%m').strftime('%B')


@router.get("/sleep-async/{seconds}", tags=["timekeeper"])
async def async_sleeper(seconds: int):
    """
    I sleep for some seconds, then return how long I slept.. Neat!
    But I'm also async, so it shoulnt block anything..
    """
    randstring = secrets.token_urlsafe(5)
    logging.info(f'Start async sleep for ({randstring}) for {seconds}')
    await async_sleep(seconds)
    logging.info(f'Ending async sleep for ({randstring}) for {seconds}')
    return f'I slept for {seconds} seconds'


@router.get("/sleep-sync/{seconds}", tags=["timekeeper"])
def sync_sleeper(seconds: int):
    """
    I'm almost like sleep-async, but I'm not async.. That means that I block python when I do nothing.
    """
    randstring = secrets.token_urlsafe(5)
    logging.info(f'Start sync sleep for ({randstring}) for {seconds}')
    sleep(seconds)
    logging.info(f'Ending sync sleep for ({randstring}) for {seconds}')
    return f'I slept for {seconds} seconds'


class TimeKeeper(Setup):
    def __init__(self, app):
        app.include_router(router)
