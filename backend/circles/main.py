import logging
from fastapi import FastAPI, Request, Header, Depends
from circles_model import InviteRequest, InviteResponse, GetResponse, InviteActionRequest, AcceptResponse, MessageResponse, ViewCircleResponse
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue    # Importing cillians DB models.

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

@app.post("/invite")
async def invite_to_circle(inbound: InviteRequest, response_class = InviteResponse) -> InviteResponse:
    logger.info(f"Create endpoint called for Circle: {inbound.inviter}")
    #THIS WILL HAVE CODE FOR CREATING AN ACTUAL INVITE DATABASE-WISE
    invite_response = InviteResponse(
        invite_id=get_invite_id(), # to be fleshed out later, placeholder
        status="pending"
    )
    return invite_response

@app.get("/get_invites", response_class = GetResponse)
async def get_invites(request: Request) -> GetResponse:
    return GetResponse([get_invite_id(), get_invite_id()+1, get_invite_id()+2])

@app.post("/accept", response_class = AcceptResponse)
async def accept_invite(inbound: InviteActionRequest) -> AcceptResponse:
    #Will add person to circle
    accept_response=AcceptResponse(
        circle_id=get_circle_id()
    )
    return accept_response

@app.post("/decline", response_class = MessageResponse)
async def decline_invite(inbound: InviteActionRequest) -> MessageResponse:
    #This will have logic for deleting an invite from the database
    decline_response=MessageResponse(
        message="foodwise wuz here"
    )
    return decline_response

@app.get("/mycircle", response_class = ViewCircleResponse)
async def view_circle(request:Request) -> ViewCircleResponse:
    return ViewCircleResponse([get_user(), get_user()+"1", get_user()+"2"])

@app.post("/remove", response_class = MessageResponse)
async def remove_from_circle(inbound:InviteRequest) -> MessageResponse:
    #This will have logic for removing an individual from a circle
    remove_response=MessageResponse(
        message="haha!"
    )
    return remove_response


