import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis 

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r_handle = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)



logging.basicConfig(level=logging.INFO, format='[proximity] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/proximity", title="proximity_service")

class RegisterRequest(BaseModel):
        user_id: int
        username: str

@app.get("/")
async def root():
    return {"Proximity Service: API called"}

#There is absolute no HTML served in the microservice, this returns a token
@app.post("/register_user")
async def register(request : RegisterRequest) -> str:
    
    r_handle.hset("user:phonebook", str(request.user_id), request.username)
    message = "f{request.user_id} {request.username}"
    return message


    


