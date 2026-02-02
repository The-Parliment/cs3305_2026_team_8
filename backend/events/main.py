import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from events_model import CreateRequest, CreateResponse
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.DatabaseClasses import Events, AttendingEvent, Venue    # Importing cillians DB models.

logging.basicConfig(level=logging.INFO, format='[events] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/events", title="events_service")


"""
def get_current_user(authorization: str =  Header(...)) -> int:
    # this is where we would call cillians verify_and_decode function.
    # to extract the user_id from the JWToken.

    Note - the issue at the moment is cillian's toke does not contain a user_id
    because the db work has to be done first...
    would alos be nice if we packed in the username/handle into that token too.
    would prevent a lot fo cross-service chater
    return 1234
"""

def get_current_user() -> int:
    return 4567

@app.get("/")
async def root():
    return {"message: Events Service API called"}

#There is absolute no HTML served in the microservice, this returns a token
@app.post("/create")
async def create_item(inbound: CreateRequest, user_id: int = Depends(get_current_user)) -> CreateResponse:
    logger.info(f"Create endpoint called for Event: {inbound.title}")
    create_response = CreateResponse
    create_response.event_id = user_id #This would be retrieved from the database
    create_response.title = inbound.title
    create_response.description = inbound.description
    create_response.date = inbound.date
    create_response.time = inbound.time
    create_response.location = inbound.location
    return create_response
