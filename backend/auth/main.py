import logging
from common.JWTSecurity import decode_and_verify
from sqlalchemy import select, insert, delete, update
from fastapi import Depends, FastAPI, HTTPException, Request
from common.JWTSecurity import decode_and_verify
from common.db import db
from common.db.db import get_db
from common.db.structures.structures import User, UserDetails
from security import mint_access_token, mint_refresh_token, verify_user
from structures import LoginRequest, MessageResponse, RegisterRequest, ResetPasswordRequest, TokenResponse, RefreshRequest, UserDetailsRequest, UserDetailsResponse, UsernameRequest
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO, format='[auth] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/auth", title="auth_service")

def get_username_from_request(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        claims = decode_and_verify(token, expected_type="access")
        return claims.get("sub")
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "Auth Service API called"}

@app.post("/register", response_model=MessageResponse)
async def register(request: RegisterRequest) -> MessageResponse:
    if get_user_exists(request.username):
        print(f"DEBUG: Registration failed - username {request.username} already exists")
        return MessageResponse(message=f"Username {request.username} already exists.", valid=False)
    if get_email_exists(request.email):
        print(f"DEBUG: Registration failed - email {request.email} already exists")
        return MessageResponse(message=f"Email {request.email} already exists.", valid=False)
    if get_phone_number_exists(request.phone_number):
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

def get_user_exists(username):
    db = get_db()
    stmt = select(User).filter_by(username=username).limit(1)
    result = db.scalar(stmt)
    return result is not None

def get_email_exists(email):
    db = get_db()
    stmt = select(UserDetails).filter_by(email=email).limit(1)
    result = db.scalar(stmt)
    return result is not None

def get_phone_number_exists(phone_number):
    db = get_db()
    stmt = select(UserDetails).filter_by(phone_number=phone_number).limit(1)
    result = db.scalar(stmt)
    return result is not None

@app.get("/user_exists", response_model=MessageResponse)
async def user_exists(user: UsernameRequest) -> MessageResponse:
    result = get_user_exists(user.username)
    return MessageResponse(message=f"User {user.username} exists: {result}", valid=result)

@app.get("/email_exists", response_model=MessageResponse)
async def email_exists(email: UsernameRequest) -> MessageResponse:
    result = get_email_exists(email.username)
    return MessageResponse(message=f"Email {email.username} exists: {result}", valid=result)

@app.get("/phone_number_exists", response_model=MessageResponse)
async def phone_number_exists(phone_number: UsernameRequest) -> MessageResponse:
    result = get_phone_number_exists(phone_number.username)
    return MessageResponse(message=f"Phone number {phone_number.username} exists: {result}", valid=result)

@app.get("/users/me", response_model=UserDetailsResponse)
async def get_user_details(request: Request, authorized_user : str = Depends(get_username_from_request)) -> UserDetailsResponse:
    db = get_db()
    stmt = select(UserDetails).filter_by(username=authorized_user).limit(1)
    result = db.scalar(stmt)
    return UserDetailsResponse(
        username=result.username,
        first_name=result.first_name,
        last_name=result.last_name,
        email=result.email,
        phone_number=result.phone_number
    )

@app.post("/users/me", response_model=MessageResponse)
async def update_user_details(request: UserDetailsRequest, authorized_user : str = Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    user_details = db.scalar(select(UserDetails).filter_by(username=authorized_user).limit(1))
    first_name = request.first_name if request.first_name else user_details.first_name
    last_name = request.last_name if request.last_name else user_details.last_name
    email = request.email if request.email else user_details.email
    phone_number = request.phone_number if request.phone_number else user_details.phone_number
    stmt = update(UserDetails).values(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number
    ).where(UserDetails.username == authorized_user)
    db.execute(stmt)
    db.commit()
    return MessageResponse(message=f"User {authorized_user} updated successfully.", valid=True)