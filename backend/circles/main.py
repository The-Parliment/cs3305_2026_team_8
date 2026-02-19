import logging
from fastapi import Depends, FastAPI, Request
from circles_model import MessageResponse, UsernameListResponse, UsersRequest
from common.JWTSecurity import decode_and_verify
from common.db.structures.structures import UserRequest, RequestTypes, Status
from common.db.db import get_db
from sqlalchemy import select, insert, delete, update

logging.basicConfig(level=logging.INFO, format='[circles] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# invite_id in this must be figured out + fleshed out later when db is working
app = FastAPI(root_path="/circles", title="circles_service")

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
    return {"message": "Circles Service API called"}

@app.post("/invite", response_model=MessageResponse)
async def invite_to_circle(inbound: UsersRequest) -> MessageResponse:
    with get_db() as db:
        stmt = insert(UserRequest).values(
            field1=inbound.inviter,
            field2=inbound.invitee,
            type=RequestTypes.CIRCLE_INVITE,
            status=Status.PENDING
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(
            message=f"Invited {inbound.invitee} to circle."
        )

@app.get("/get_invites", response_model=UsernameListResponse)
async def get_invites(request: Request, authorized_user: str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    with get_db() as db:
        this_user = authorized_user
        result = select(UserRequest.field1).filter_by(field2=this_user, 
                                                    type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING)
        users = db.scalars(result).all()
        return UsernameListResponse(user_names=users)

@app.get("/get_invites_sent", response_model=UsernameListResponse)
async def get_invites_sent(request: Request, authorized_user: str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    this_user = authorized_user
    with get_db() as db:
        result = select(UserRequest.field2).filter_by(field1=this_user, 
                                                 type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING)
        users = db.scalars(result).all()
        return UsernameListResponse(user_names=users)

@app.post("/accept", response_model=MessageResponse)
async def accept_invite(inbound: UsersRequest) -> MessageResponse:
    with get_db() as db:
        stmt = update(UserRequest).values(
            field1=inbound.inviter,
            field2=inbound.invitee,
            type=RequestTypes.CIRCLE_INVITE,
            status=Status.ACCEPTED
        ).where(
            UserRequest.field1 == inbound.inviter, 
            UserRequest.field2 == inbound.invitee, 
            UserRequest.type == RequestTypes.CIRCLE_INVITE,
            UserRequest.status == Status.PENDING)
        db.execute(stmt)
        db.commit()
        return MessageResponse(
            message=f"Joined {inbound.inviter}'s circle."
        )

@app.post("/decline", response_model=MessageResponse)
async def decline_invite(inbound: UsersRequest) -> MessageResponse:
    with get_db() as db:
        stmt = delete(UserRequest).where(
            UserRequest.field1 == inbound.inviter,
            UserRequest.field2 == inbound.invitee,
            UserRequest.type == RequestTypes.CIRCLE_INVITE,
            UserRequest.status == Status.PENDING)
        db.execute(stmt)
        db.commit()
        return MessageResponse(
            message=f"Invite to join {inbound.inviter}'s circle has been rejected."
        )

@app.get("/mycircle", response_model=UsernameListResponse)
async def get_circle(request:Request, authorized_user: str = Depends(get_username_from_request)) -> UsernameListResponse:
    if not authorized_user:
        return MessageResponse(message="Unauthorized", valid=False)
    with get_db() as db:
        this_user = authorized_user
        result = select(UserRequest.field2).filter_by(field1=this_user, 
                                                type=RequestTypes.CIRCLE_INVITE, status=Status.ACCEPTED)
        names = db.scalars(result).all()
        return UsernameListResponse(user_names=names)

@app.post("/remove", response_model=MessageResponse)
async def remove_from_circle(inbound:UsersRequest) -> MessageResponse:
    with get_db() as db:
        stmt = delete(UserRequest).where(
            UserRequest.field1 == inbound.inviter,
            UserRequest.field2 == inbound.invitee,
            UserRequest.type == RequestTypes.CIRCLE_INVITE,
            UserRequest.status == Status.ACCEPTED)
        db.execute(stmt)
        db.commit()
        return MessageResponse(
            message=f"{inbound.invitee} has been removed from your circle."
        )
