from pydantic import BaseModel
from datetime import datetime

class CreateRequest(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    datetime_start: datetime
    datetime_end: datetime
    venue: str
    host:str

class CreateResponse(BaseModel):
    event_id: int
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    venue: str

class MessageResponse(BaseModel):
    message: str

class ListResponse(BaseModel):
    list: list

class InfoResponse(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    datetime_start: datetime
    datetime_end: datetime
    venue: str
    host:str

class InviteRequest(BaseModel):
    inviter:str
    event_id: int

class CancelRequest(BaseModel):
    event_id: int

class EditRequest(BaseModel):
    event_id: int
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    latitude: float
    longitude: float
    venue_id: int