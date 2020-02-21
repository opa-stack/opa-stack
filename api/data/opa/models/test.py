from typing import List, Optional

from pydantic import Field

from .mixins import DateTimeModelMixin


class Item(DateTimeModelMixin):
    s: str = ""
    tagList: List[str] = Field([])
    string: str
    number: float
    boolean: bool = False


class Items(DateTimeModelMixin):
    items: List[Item]
    meta: str
