from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DateTimeModelMixin(BaseModel):
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
