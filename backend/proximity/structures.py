from pydantic import BaseModel
from datetime import datetime

class RegisterRequest(BaseModel):
    user_id: int
    username: str

class UpdateLocationRequest(BaseModel):
    username: str
    latitude: float
    longitude: float

class GetFriendsRequest(UpdateLocationRequest):
    radius: float

class Friend(BaseModel):
    username: str
    latitude: float
    longitude: float
    distance: float
    datetime: datetime

class FriendsList(BaseModel):
    friends: list[Friend]
    count: int