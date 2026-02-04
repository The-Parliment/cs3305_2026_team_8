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
@app.post("/create")
async def create_item(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    logger.info(f"Create endpoint called for Event: {inbound.title}")
    create_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    events.append(create_response)
    return create_response

@app.post("/eventinfo")
async def event_info(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    event_info_response = CreateResponse( 
        event_id = user_id, # this is currently invalid
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return event_info_response


@app.post("/search")
async def search_events(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    search_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return search_response 

@app.post("/rsvp")
async def rsvp_events(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    rsvp_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return rsvp_response 

@app.post("/invitecircle")
async def invite_circle(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    invite_circle_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return invite_circle_response 

@app.post("/invitegroup")
async def invite_group(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    invite_group_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return invite_group_response 

@app.post("/cancel")
async def cancel_event(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    cancel_event_response = CreateResponse ( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return cancel_event_response

@app.post("/edit")
async def edit_event(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    edit_event_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return edit_event_response

@app.post("/myevents")
async def my_events(inbound: CreateRequest, user_id: int = Depends(get_current_user), response_model = CreateResponse) -> CreateResponse:
    my_events_response = CreateResponse( 
        event_id = user_id,
        title = inbound.title,
        description = inbound.description,
        datetime_start = inbound.datetime_start,
        datetime_end = inbound.datetime_end,
        venue = inbound.venue)
    return my_events_response