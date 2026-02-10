import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis 
from tokens import get_username

VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))
valkey_client = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, decode_responses=True)

logging.basicConfig(level=logging.INFO, format='[proximity] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/proximity", title="proximity_service")

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

@app.get("/")
async def root():
    return {"Proximity Service: API called"}

#There is absolute no HTML served in the microservice, this returns a token
@app.post("/register_user")
async def register(requester : RegisterRequest) -> str:
    
    valkey_client.hset("user:phonebook", str(requester.user_id), requester.username)
    message = f"{requester.user_id} {requester.username}"
    return message

# This endpoint will update the latitude and longitude of the user.
@app.post("/update_location")
async def update_location(requester: UpdateLocationRequest) -> str:
    username = get_username(requester.username)
    valkey_client.geoadd("user:locations", (requester.longitude, requester.latitude, username))
    message = f"Location updated for {username}: ({requester.latitude}, {requester.longitude})"
    return message

@app.post("/get_friends")
async def get_friends(requester: GetFriendsRequest) -> FriendsList:
    username = get_username(requester.username)
    everyones_location = valkey_client.georadius("user:locations", requester.longitude, 
                                         requester.latitude, requester.radius, unit='km', 
                                         withdist=True, withcoord=True)
    
    '''
    At the moment, what follows returns everyone. When the circle service can give me a list of my friends, I can use
    that list to filter what is returned from georadius
    '''
    friends_list = []
    for friend in everyones_location:
        friend_username = friend[0]
        if friend_username == username:
            continue  # Skip the caller
        friend_distance = friend[1]
        # The [2] returned is called coordinates, which itself is an array of [longitude, latitude]
        friend_latitude = friend[2][1]
        friend_longitude = friend[2][0]
        friends_list.append(Friend(username=friend_username, latitude=friend_latitude, 
                                   longitude=friend_longitude, distance=friend_distance))
    return FriendsList(friends=friends_list, count=len(friends_list))
