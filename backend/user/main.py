import logging
from fastapi import Depends, FastAPI, HTTPException, Request
from common.JWTSecurity import decode_and_verify
from user_model import MessageResponse, UsernameListResponse, UsernameRequest, UsersRequest
from common.db.structures.structures import User, UserDetails, UserRequest, RequestTypes, Status
from common.db.db import get_db
from sqlalchemy import select, insert, delete, update

logging.basicConfig(level=logging.INFO, format='[user] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/user", title="user_service")

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
    return {"message": "User Service API called"}

@app.post("/send_follow_request", response_model=MessageResponse)
async def send_follow_request(inbound: UsersRequest) -> MessageResponse:
    db = get_db()
    stmt = insert(UserRequest).values(
        field1=inbound.inviter,
        field2=inbound.invitee,
        type=RequestTypes.FOLLOW_REQUEST,
        status=Status.PENDING
    )
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"Sent follow request to {inbound.invitee}."
    )

@app.get("/get_follow_requests_received", response_model=UsernameListResponse)
async def get_follow_requests_received(request: Request, authorized_user : str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    db = get_db()
    result = select(UserRequest.field1).filter_by(field2=authorized_user, 
                                                type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    users = db.scalars(result).all()
    return UsernameListResponse(user_names=users)

@app.get("/get_follow_requests_sent", response_model=UsernameListResponse)
async def get_follow_requests_sent(request: Request, authorized_user : str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=authorized_user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    users = db.scalars(result).all()
    return UsernameListResponse(user_names=users)

@app.post("/accept_follow_request", response_model=MessageResponse)
async def accept_follow_request(inbound: UsersRequest) -> MessageResponse:
    db = get_db()
    stmt = update(UserRequest).values(
        field1=inbound.inviter,
        field2=inbound.invitee,
        type=RequestTypes.FOLLOW_REQUEST,
        status=Status.ACCEPTED
    ).where(
        UserRequest.field1 == inbound.inviter, 
        UserRequest.field2 == inbound.invitee, 
        UserRequest.type == RequestTypes.FOLLOW_REQUEST,
        UserRequest.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"{inbound.invitee} accepted follow request from {inbound.inviter}."
    )

@app.post("/decline_follow_request", response_model=MessageResponse)
async def decline_follow_request(inbound: UsersRequest) -> MessageResponse:
    db = get_db()
    stmt = delete(UserRequest).where(
        UserRequest.field1 == inbound.inviter,
        UserRequest.field2 == inbound.invitee,
        UserRequest.type == RequestTypes.FOLLOW_REQUEST,
        UserRequest.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"Follow request from {inbound.inviter} has been declined."
    )

@app.get("/followers", response_model=UsernameListResponse)
async def get_followers(request:Request, authorized_user : str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    db = get_db()
    result = select(UserRequest.field1).filter_by(field2=authorized_user, 
                                            type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    names = db.scalars(result).all()
    return UsernameListResponse(user_names=names)

@app.get("/following", response_model=UsernameListResponse)
async def get_following(request:Request, authorized_user : str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=authorized_user, 
                                            type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    names = db.scalars(result).all()
    return UsernameListResponse(user_names=names)

@app.get("/friends", response_model=UsernameListResponse)
async def get_friends(request:Request, authorized_user : str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=authorized_user, 
                                            type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    
    people_user_one_follows = db.scalars(result).all()
    friends = []
    for name in people_user_one_follows:
        stmt = select(UserRequest).filter_by(field1=name, field2=authorized_user, 
                                            type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
        result = db.scalar(stmt)
        if result:
            friends.append(name)
    return UsernameListResponse(user_names=friends)

@app.post("/withdraw_follow_request", response_model=MessageResponse)
async def withdraw(inbound:UsersRequest) -> MessageResponse:
    db = get_db()
    stmt = delete(UserRequest).where(
        UserRequest.field1 == inbound.inviter,
        UserRequest.field2 == inbound.invitee,
        UserRequest.type == RequestTypes.FOLLOW_REQUEST,
        UserRequest.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"{inbound.invitee} has been withdrawn."
    )

@app.post("/unfollow", response_model=MessageResponse)
async def unfollow(inbound:UsersRequest) -> MessageResponse:
    db = get_db()
    stmt = delete(UserRequest).where(
        UserRequest.field1 == inbound.inviter,
        UserRequest.field2 == inbound.invitee,
        UserRequest.type == RequestTypes.FOLLOW_REQUEST,
        UserRequest.status == Status.ACCEPTED)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"{inbound.invitee} has been unfollowed."
    )

@app.get("/list_users", response_model=UsernameListResponse)
async def list_all_users(request: Request) -> UsernameListResponse:
    db = get_db()
    result = select(User.username)
    names = db.scalars(result).all()
    return UsernameListResponse(user_names=names)
