from typing import List

from fastapi import APIRouter, Body, Depends
from starlette.status import HTTP_201_CREATED
from starlette.requests import Request

from opa.models.test import Item, Items

from opa.core.security import get_src_zone, Zone
from opa.db.mongodb import AsyncIOMotorClient, get_database

from opa.core.config import database_name


async def create_test_item(conn: AsyncIOMotorClient, item: Item) -> Item:
    item.s = item.string
    item_doc = item.dict()
    await conn[database_name]["test"].insert_one(item_doc)
    return Item(**item_doc)


async def read_all_items(conn: AsyncIOMotorClient) -> List[Item]:
    items: List[Item] = []
    rows = conn[database_name]["test"].find()
    async for row in rows:
        items.append(Item(**row))
    return items


router = APIRouter()


@router.get("/demo-route-string", tags=["demo"])
def return_string():
    return 'test ok'


from demo_util import double


@router.get("/demo-route-util", tags=["demo"])
def return_from_util():
    return f'From demo_util.double: {double(3)}'


@router.post(
    "/demo-route", response_model=Item, tags=["demo"], status_code=HTTP_201_CREATED
)
async def create_item(
    item: Item = Body(..., embed=True),
    zone: Zone = Depends(get_src_zone),
    db: AsyncIOMotorClient = Depends(get_database),
):
    return await create_test_item(db, item)


@router.get("/demo-route", response_model=Items, tags=["demo"])
async def get_all_items(
    zone: Zone = Depends(get_src_zone), db: AsyncIOMotorClient = Depends(get_database)
):
    return {'items': await read_all_items(db), 'meta': 'abc'}


@router.get("/demo-requestdata", tags=["demo"])
async def get_requestdata(request: Request):
    return {"ip": request.client.host}


def setup(app, **kwargs):
    app.include_router(router)
