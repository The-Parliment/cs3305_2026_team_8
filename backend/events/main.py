import logging
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from events_model import CreateRequest, CreateResponse, SearchResponse, InfoResponse, SearchEvent, RSVPRequest, RSVPResponse, InviteRequest, InviteResponse, CancelRequest, CancelResponse, EditRequest, MyEventsResponse
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.DatabaseClasses import Events, AttendingEvent, Venue    # Importing cillians DB models.

logging.basicConfig(level=logging.INFO, format='[events] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/events", title="events_service")

# all placeholder code until it is possible to work with db
# code is currently so vague it is identical
# all placeholder code until it is possible to work with db
# code is currently so vague it is identical

"""
def get_current_user(authorization: str =  Header(...)) -> int:
    this is where we would call cillians verify_and_decode function.
    to extract the user_id from the JWToken.
    this is where we would call cillians verify_and_decode function.
    to extract the user_id from the JWToken.

    Note - the issue at the moment is cillian's token does not contain a user_id
    Note - the issue at the moment is cillian's token does not contain a user_id
    because the db work has to be done first...
    would also be nice if we packed in the username/handle into that token too.
    would prevent a lot of cross-service chatter
    would also be nice if we packed in the username/handle into that token too.
    would prevent a lot of cross-service chatter
    return 1234
"""

events = []

events = []

def get_current_user() -> int:
    return 4567

def get_venue_id() -> int:
    return 1234

def get_event_id() -> int:
    return 3456

@app.get("/")
async def root():
    return {"message": "Events Service API called"}
    return {"message": "Events Service API called"}

#There is absolute no HTML served in the microservice, this returns a token
@app.post("/create", response_class = CreateResponse)
async def create_item(inbound: CreateRequest, event_id: int= Depends(get_event_id)) -> CreateResponse:
    logger.info(f"Create endpoint called for Event: {inbound.title}")
    create_response = CreateResponse( 
        event_id = event_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    events.append(create_response) # add to database
    return create_response

@app.get("/eventinfo", response_class = InfoResponse)
async def event_info(request: Request) -> InfoResponse:
    return InfoResponse() #to be filled out later


@app.get("/search", response_class = SearchResponse)
async def search_events(request:Request) -> SearchResponse:
    return SearchResponse(SearchEvent(), SearchEvent(), SearchEvent()) # needs to be filled out + restructured for scaling
    

@app.post("/rsvp", response_class = RSVPResponse)
async def rsvp_events(inbound: RSVPRequest) -> RSVPResponse:
    rsvp_response = RSVPResponse( 
        message="foodwise wuz here",
        status="pending"
        )
    return rsvp_response 

@app.post("/invitecircle", response_class = InviteResponse)
async def invite_circle(inbound: InviteRequest) -> InviteResponse:
    invite_circle_response = InviteResponse( 
        message="Hello everypony",
        )
    return invite_circle_response 

@app.post("/invitegroup", response_class = InviteResponse)
async def invite_group(inbound: InviteRequest) -> InviteResponse:
    invite_group_response = InviteResponse( 
        message="Hi single pony",
        )
    return invite_group_response 

@app.post("/cancel", response_class = CancelResponse)
async def cancel_event(inbound: CancelRequest) -> CancelResponse:
    cancel_event_response = CancelResponse( 
        message="No way!",
        status="cancelled")
    return cancel_event_response

@app.put("/edit", response_class = InfoResponse)
async def edit_event(inbound: EditRequest, event_id: int =Depends(get_event_id), venue: int = Depends(get_venue_id)) -> InfoResponse:
    edit_event_response = InfoResponse( 
        event_id=event_id,
        title=inbound.title,
        description=inbound.description,
        datetime_start=inbound.datetime_start,
        datetime_end=inbound.datetime_end,
        latitude=inbound.latitude,
        longitude=inbound.longitude,
        venue_id=venue)
    return edit_event_response


@app.get("/myevents", response_class = MyEventsResponse)
async def my_events(request:Request) -> MyEventsResponse:
    return MyEventsResponse(CreateResponse(), CreateResponse(), CreateResponse())