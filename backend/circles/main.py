import logging
from fastapi import FastAPI, Request, Header, Depends
from circles_model import InviteRequest, InviteResponse, GetResponse, InviteActionRequest, AcceptResponse, MessageResponse, ViewCircleResponse
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue, Request, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from sqlalchemy import select, insert, delete, update

logging.basicConfig(level=logging.INFO, format='[circles] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# invite_id in this must be figured out + fleshed out later when db is working
app = FastAPI(root_path="/circles", title="circles_service")

def get_current_user() -> str:
    return "pee"

def get_user() -> str:
    return "poo"

def get_invite_id() -> int:
    return 1234

def get_circle_id() -> int:
    return 7890

@app.get("/")
async def root():
    return {"message": "Circles Service API called"}

@app.post("/invite", response_class = InviteResponse)
async def invite_to_circle(inbound: InviteRequest) -> InviteResponse:
    db = get_db()
    stmt = insert(Request).values(
        field1=inbound.inviter,
        field2=inbound.invitee,
        type=RequestTypes.CIRCLE_INVITE,
        status=Status.PENDING
    )
    db.execute(stmt)
    db.commit()
    invite_response = InviteResponse(
        invite_id=hash(inbound.inviter + inbound.invitee), #Temp
        status="pending"
    )
    return invite_response

@app.get("/get_invites", response_class = GetResponse)
async def get_invites(request: Request) -> GetResponse:
    return GetResponse([get_invite_id(), get_invite_id()+1, get_invite_id()+2])

@app.post("/accept", response_class = AcceptResponse)
async def accept_invite(inbound: InviteActionRequest) -> AcceptResponse:
    db = get_db()
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
    accept_response=AcceptResponse(
        circle_id=get_circle_id()
    )
    return accept_response

@app.post("/decline", response_class = MessageResponse)
async def decline_invite(inbound: InviteActionRequest) -> MessageResponse:
    db = get_db()
    stmt = delete(Request).where(
        Request.field1 == inbound.inviter,
        Request.field2 == inbound.invitee,
        Request.type == RequestTypes.CIRCLE_INVITE,
        Request.status == Status.PENDING)
    db.execute(stmt)
    db.commit()
    decline_response=MessageResponse(
        message="foodwise wuz here"
    )
    return decline_response

@app.get("/mycircle", response_class = ViewCircleResponse)
async def get_circle(request:Request) -> ViewCircleResponse:
    return ViewCircleResponse([get_user(), get_user()+"1", get_user()+"2"])

@app.post("/remove", response_class = MessageResponse)
async def remove_from_circle(inbound:InviteRequest) -> MessageResponse:
    #This will have logic for removing an individual from a circle
    remove_response=MessageResponse(
        message="haha!"
    )
    return remove_response
