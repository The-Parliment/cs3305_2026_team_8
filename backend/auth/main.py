import logging
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='[auth_service] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class User(BasModel):
    username: str
    password: str

@app.get("/")
def root():
    logger.info("API called: / (root endpoint)")
    return {"message: API called"}

@app.post("/register")
def register(user: User):
    logger.info(f"Registration endpoint called for user: {user.username}")
    # Return both username and password for demonstration (not secure in real apps)
    return {
        "message": f"Register called for {user.username}",
        "username": user.username,
        "password": user.password
    }

@app.post("/login")
def login(user: User):
    logger.info(f"Login endpoint called for user: {user.username}")
    # Return both username and password for demonstration (not secure in real apps)
    return {
        "message": f"Login called for {user.username}",
        "username": user.username,
        "password": user.password
    }

