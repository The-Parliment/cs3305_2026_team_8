import logging
from fastapi import FastAPI, Request, Header, Depends
from circles_model import MessageResponse, UsernameListResponse, CircleRequest
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue, Request, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from common.clients.user import user_exists
from sqlalchemy import select, insert, delete, update
import json

logging.basicConfig(level=logging.INFO, format='[circles] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# invite_id in this must be figured out + fleshed out later when db is working
app = FastAPI(root_path="/circles", title="circles_service")

@app.get("/")
async def root():
    return {"message": "Circles Service API called"}

@app.post("/invite", response_class = MessageResponse)
async def invite_to_circle(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
    stmt = insert(Request).values(
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

@app.get("/get_invites", response_class = UsernameListResponse)
async def get_invites(request: Request, claims:dict) -> UsernameListResponse:
    db = get_db()
    user = claims.get("sub")
    result = select(Request.field1).filter_by(field2=user, 
                                                type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING)
    users = db.scalars(result).all()
    return UsernameListResponse(users)

@app.post("/accept", response_class = MessageResponse)
async def accept_invite(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
    stmt = update(Request).values(
        field1=inbound.inviter,
        field2=inbound.invitee,
        type=RequestTypes.CIRCLE_INVITE,
        status=Status.ACCEPTED
    ).where(
        Request.field1 == inbound.inviter, 
        Request.field2 == inbound.invitee, 
        Request.type == RequestTypes.CIRCLE_INVITE,
        Request.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"Joined {inbound.inviter}'s circle."
    )

@app.post("/decline", response_class = MessageResponse)
async def decline_invite(inbound: CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
    stmt = delete(Request).where(
        Request.field1 == inbound.inviter,
        Request.field2 == inbound.invitee,
        Request.type == RequestTypes.CIRCLE_INVITE,
        Request.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"Invite to join {inbound.inviter}'s circle has been rejected."
    )

@app.get("/mycircle", response_class = UsernameListResponse)
async def get_circle(request:Request, claims:dict) -> UsernameListResponse:
    db = get_db()
    user = claims.get("sub")
    result = select(Request.field2).filter_by(field1=user, 
                                              type=RequestTypes.CIRCLE_INVITE, status=Status.ACCEPTED)
    return UsernameListResponse(db.scalars(result).all())

@app.post("/remove", response_class = MessageResponse)
async def remove_from_circle(inbound:CircleRequest) -> MessageResponse:
    db = get_db()
    if not user_exists(inbound.inviter):
        return MessageResponse(f"User {inbound.inviter} does not exist.")
    if not user_exists(inbound.invitee):
        return MessageResponse(f"User {inbound.invitee} does not exist.")
    stmt = delete(Request).where(
        Request.field1 == inbound.inviter,
        Request.field2 == inbound.invitee,
        Request.type == RequestTypes.CIRCLE_INVITE,
        Request.status == Status.ACCEPTED)
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"{inbound.invitee} has been removed from your circle."
    )
