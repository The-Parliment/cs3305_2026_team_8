import logging
from common.JWTSecurity import decode_and_verify
from sqlalchemy import select, insert, delete, update
from fastapi import FastAPI, HTTPException
from common.JWTSecurity import decode_and_verify
from common.db.db import get_db
from common.db.structures.structures import User, UserDetails
from security import mint_access_token, mint_refresh_token, verify_user
from structures import LoginRequest, MessageResponse, RegisterRequest, TokenResponse, RefreshRequest, UsernameRequest
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO, format='[auth] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/auth", title="auth_service")

@app.get("/")
async def root():
    return {"message": "Auth Service API called"}

@app.post("/register", response_model=MessageResponse)
async def register(request: RegisterRequest) -> MessageResponse:
    if user_exists(request.username):
        print(f"DEBUG: Registration failed - username {request.username} already exists")
        return MessageResponse(message=f"Username {request.username} already exists.", valid=False)
    if email_exists(request.email):
        print(f"DEBUG: Registration failed - email {request.email} already exists")
        return MessageResponse(message=f"Email {request.email} already exists.", valid=False)
    if phone_number_exists(request.phone_number):
        print(f"DEBUG: Registration failed - phone number {request.phone_number} already exists")
        return MessageResponse(message=f"Phone number {request.phone_number} already exists.", valid=False)
    db = get_db()
    new_user = User(username=request.username, hashed_password=pwd.hash(request.password))
    new_user_details = UserDetails(username=request.username, first_name=request.first_name, 
                                   last_name=request.last_name, email=request.email, 
                                   phone_number=request.phone_number)
    db.add(new_user)
    db.add(new_user_details)
    db.commit()
    print(f"DEBUG: User {request.username} registered successfully")
    return MessageResponse(message=f"User {request.username} registered successfully.", valid=True)

@app.post("/login", response_model=TokenResponse)
async def login(request : LoginRequest) -> TokenResponse:
    if not verify_user(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access = mint_access_token(subject=request.username, extra_claims={"roles": ["user"]})
    refresh = mint_refresh_token(subject=request.username)

    return TokenResponse(access_token=access, refresh_token=refresh)

@app.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest) -> TokenResponse:
    try:
        payload = decode_and_verify(req.refresh_token, expected_type="refresh")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = mint_access_token(subject=payload["sub"], extra_claims={"roles": payload.get("roles", ["user"])})
    return TokenResponse(access_token=access, refresh_token=req.refresh_token)

@app.get("/user_exists", response_model=MessageResponse)
async def user_exists(user: UsernameRequest) -> MessageResponse:
    db = get_db()
    stmt = select(User).filter_by(username=user.username).limit(1)
    result = db.scalar(stmt)
    return MessageResponse(message=f"User {user.username} exists: {result is not None}", valid=result is not None)

@app.get("/email_exists", response_model=MessageResponse)
async def email_exists(email: UsernameRequest) -> MessageResponse:
    db = get_db()
    stmt = select(UserDetails).filter_by(email=email.username).limit(1)
    result = db.scalar(stmt)
    return MessageResponse(message=f"Email {email.username} exists: {result is not None}", valid=result is not None)

@app.get("/phone_number_exists", response_model=MessageResponse)
async def phone_number_exists(phone_number: UsernameRequest) -> MessageResponse:
    db = get_db()
    stmt = select(UserDetails).filter_by(phone_number=phone_number.username).limit(1)
    result = db.scalar(stmt)
    return MessageResponse(message=f"Phone number {phone_number.username} exists: {result is not None}", valid=result is not None)
