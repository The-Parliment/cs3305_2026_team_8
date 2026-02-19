from pydantic import BaseModel
from datetime import datetime

class CreateRequest(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    datetime_start: datetime
    datetime_end: datetime
    venue: str
    host: str | None = ""
    public: bool | None = False

class CreateResponse(BaseModel):
    event_id: int

class MessageResponse(BaseModel):
    message: str
    valid : bool | None = True

class ListResponse(BaseModel):
    lst: list

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
    public: bool

class ListEventResponse(BaseModel):
    events: list[InfoResponse]

class InviteResponse(BaseModel):
    event_id: int
    username: str
    title: str

class ListInviteResponse(BaseModel):
    invites: list[InviteResponse]

class InviteRequest(BaseModel):
    event_id: int

class CancelRequest(BaseModel):
    event_id: int
    
class BooleanResponse(BaseModel):
    value: bool

class EditRequest(BaseModel):
    title: str
    description: str
    datetime_start: datetime
    datetime_end: datetime
    latitude: float
    longitude: float
    venue: str
    public: bool | None = False