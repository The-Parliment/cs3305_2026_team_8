from pydantic import BaseModel
from datetime import date, time

class CreateRequest(BaseModel):
    title: str
    description: str
    date: date
    time: time
    location: str

class CreateResponse(BaseModel):
    event_id: int
    title: str
    description: str
    date: date
    time: time
    location: str

