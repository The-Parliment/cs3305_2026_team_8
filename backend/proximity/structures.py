from pydantic import BaseModel

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

class FriendsList(BaseModel):
    friends: list[Friend]
    count: int