from pydantic import BaseModel
from datetime import datetime

class CreateRequest(BaseModel):
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    venue: str

class CreateResponse(BaseModel):
    event_id: int
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    venue: str

