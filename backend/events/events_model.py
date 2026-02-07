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


class InfoResponse(BaseModel):
    event_id: int
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    latitude: float
    longitude: float
    venue_id: int

class SearchEvent(BaseModel):
    event_id: int
    title: str
    datetime_start: datetime
    datetime_end: datetime
    latitude: float
    longitude: float
    venue_id: int

class SearchResponse(BaseModel):
    events: list

class RSVPRequest(BaseModel):
    event_id: int
    status: str

class RSVPResponse(BaseModel):
    message: str
    status: str

class InviteRequest(BaseModel):
    event_id: int

class InviteResponse(BaseModel):
    message: str

class CancelRequest(BaseModel):
    event_id: int

class CancelResponse(BaseModel):
    message: str
    status: str

class EditRequest(BaseModel):
    event_id: int
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    latitude: float
    longitude: float
    venue_id: int

class MyEventsResponse():
    events: list