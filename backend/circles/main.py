import logging
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from circles_model import MessageResponse, UsernameListResponse, CircleRequest
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue, UserRequest, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from common.clients.user import user_exists
from sqlalchemy import select, insert, delete, update
import json

logging.basicConfig(level=logging.INFO, format='[circles] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# invite_id in this must be figured out + fleshed out later when db is working
app = FastAPI(root_path="/circles", title="circles_service")

def get_user_claims(request: Request) -> dict:
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401)

    return decode_and_verify(token=access, expected_type="access")

def invitations_sent(user):
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=user, 
                                             type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING)
    return db.scalars(result).all()

@app.get("/")
async def root():
    return {"message": "Circles Service API called"}

@app.post("/invite", response_model=MessageResponse)
async def invite_to_circle(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
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
async def get_invites(request: Request) -> UsernameListResponse:
    db = get_db()
    user = get_user_claims(request).get("sub")
    result = select(UserRequest.field1).filter_by(field2=user, 
                                                type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING)
    users = db.scalars(result).all()
    return UsernameListResponse(user_names=users)

@app.get("/get_invites_sent", response_model=UsernameListResponse)
async def get_invites_sent(request: Request) -> UsernameListResponse:
    user = get_user_claims(request).get("sub")
    users = invitations_sent(user)
    return UsernameListResponse(user_names=users)

@app.post("/accept", response_model=MessageResponse)
async def accept_invite(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
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
async def decline_invite(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
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
async def get_circle(request:Request) -> UsernameListResponse:
    db = get_db()
    user = get_user_claims(request).get("sub")
    result = select(UserRequest.field2).filter_by(field1=user, 
                                            type=RequestTypes.CIRCLE_INVITE, status=Status.ACCEPTED)
    names = db.scalars(result).all()
    return UsernameListResponse(user_names=names)

@app.post("/remove", response_model=MessageResponse)
async def remove_from_circle(inbound:CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
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
