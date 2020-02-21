from starlette.requests import Request
from pydantic import BaseModel, Schema


class Zone(BaseModel):
    name: str


def get_src_zone(request: Request):
    print('get_src_zone')
    print(request.client.host)
