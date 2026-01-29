import jwt
import datetime
import logging
from fastapi import FastAPI, Header
from fastapi import Depends, HTTPException
import hashlib
from pydantic import BaseModel
 

from sqlalchemy.orm import Session
from database.tables import User as DBUser
from .db import SessionLocal



logging.basicConfig(level=logging.INFO, format='[auth_service] %(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(root_path="/auth")

# Pydantic models for inbound reg request
class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str

# Pydantic model for inbound login request
class UserLogin(BaseModel):
    username: str
    password: str

# Secret key for JWT (in production, use env var)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Function to create JWT token. data is a dict with user info - whatever you want to encode.
def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token - simply decodes it and checks expiry
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    logger.info("API called: / (root endpoint)")
    return {"message": "API called"}


# Simple CRUD endpoints for user registration.
# inbound password is hashed using SHA256 for storage.
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration endpoint called for user: {user.username}")
    # Check if user exists
    if db.query(DBUser).filter(DBUser.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "message": f"Register called for {user.username}",
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone
    }


# Login endpoint - verifies user credentials and returns JWT token if valid
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login endpoint called for user: {user.username}")
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if not db_user:
        return {"success": False, "message": "Invalid username or password"}
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if db_user.hashed_password != hashed_password:
        return {"success": False, "message": "Invalid username or password"}
    # Generate JWT token
    token = create_access_token({"sub": db_user.email})
    return {"success": True, "message": f"Login successful for {user.username}", "token": token}


@app.get("/me")
def get_my_details(token: str = Header(...), db: Session = Depends(get_db)):
    logger.info(f"Get my details endpoint called with token")
    payload = verify_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    db_user = db.query(DBUser).filter(DBUser.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "username": db_user.username,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "email": db_user.email,
        "phone": db_user.phone_number
    }
