import logging
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from events_model import CreateRequest, InfoResponse, MessageResponse, ListResponse, InviteRequest, CancelRequest, EditRequest
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue, UserRequest, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from events_database import event_exists
from sqlalchemy import select, insert, delete, update

logging.basicConfig(level=logging.INFO, format='[events] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/events", title="events_service")

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
    return {"message": "Events Service API called"}

@app.post("/create", response_model = MessageResponse)
async def create_item(inbound: CreateRequest) -> MessageResponse:
    logger.info(f"Create endpoint called for Event: {inbound.title}")
    db = get_db()
    stmt= insert(Events).values(
        id=inbound.id,
        venue=inbound.venue,
        latitude=inbound.latitude,
        longitude=inbound.longitude,
        title=inbound.title,
        description=inbound.description,
        datetime_start=inbound.datetime_start,
        datetime_end=inbound.datetime_end,
        host=inbound.host
    )
    db.execute(stmt)
    db.commit()
    create_response=MessageResponse( 
        message = "Event Created"
        )
    return create_response

@app.get("/eventinfo/{event_id}", response_model = InfoResponse)
async def event_info(request: Request, event_id:int):
    db=get_db()
    result=select(Events).filter_by(id=event_id).limit(1)
    event=db.scalar(result)
    if not event:
        return MessageResponse(message="Event not found", valid=False)
    return InfoResponse(id=event.id, 
                        venue=event.venue, 
                        latitude=event.latitude, 
                        longitude=event.longitude,
                        datetime_start=event.datetime_start, 
                        datetime_end=event.datetime_end, 
                        title=event.title, 
                        description=event.description, 
                        host=event.host)

# too complicated to fill out with rest of them
@app.get("/search", response_model = ListResponse)
async def search_events(request:Request) -> ListResponse:
    db=get_db()
    result=select(Events).filter_by
    return ListResponse() # needs to be filled out + restructured for scaling

@app.post("/invite/{username}", response_model=MessageResponse)
async def invite_user(inbound: InviteRequest, username:int) -> MessageResponse:
    db = get_db()
    stmt = insert(UserRequest).values(
        field1=inbound.inviter,
        field2=username,
        field3=inbound.event_id,
        type=RequestTypes.EVENT_INVITE,
        status=Status.PENDING
    )
    db.execute(stmt)
    db.commit()
    return MessageResponse(
        message=f"Invited {username} to event."
    )

@app.post("/invitecircle", response_model = MessageResponse)
async def invite_circle(inbound: InviteRequest) -> MessageResponse:
    db = get_db()
    stmt=select(UserRequest.field2).filter_by(
        field1=inbound.inviter,
        type=RequestTypes.CIRCLE_INVITE,
        status=Status.CONFIRMED
    )
    circle_members=db.execute(stmt).scalars().all()
    if not circle_members:
        return MessageResponse("There is nobody in your circle...")
    
    for member in circle_members:
        db.execute(insert(UserRequest).values(
        field1=inbound.inviter,
        field2=member,
        field3=inbound.event_id,
        type=RequestTypes.EVENT_INVITE,
        status=Status.PENDING
    ))
    db.commit()
    return MessageResponse("invited " + len(circle_members) +" to your event!")


#cannot complete group code without darrens code
@app.post("/invitegroup", response_model = MessageResponse)
async def invite_group(inbound: InviteRequest) -> MessageResponse:
    invite_group_response = MessageResponse( 
        message="foodwise wuz here",
        )
    return invite_group_response 

@app.post("/cancel", response_model = MessageResponse)
async def cancel_event(inbound: CancelRequest) -> MessageResponse:
    db = get_db()
    if not event_exists(inbound.event_id):
        return MessageResponse(message="There is no such event")
    stmt=delete(Events).where(
        id=inbound.event_id
    )
    db.execute(stmt)
    db.commit()
    cancel_event_response = MessageResponse( 
        message="Event deleted :(")
    return cancel_event_response

@app.put("/edit", response_model = MessageResponse)
async def edit_event(inbound: EditRequest) -> MessageResponse:
    db = get_db()
    stmt = update(Events).values(
        title=inbound.title,
        description=inbound.description,
        datetime_start=inbound.datetime_start,
        datetime_end=inbound.datetime_end,
        latitude=inbound.latitude,
        longitude=inbound.longitude,
        venue_id=inbound.venue_id).where(Events.id == inbound.event_id)
    db.execute(stmt)
    db.commit()
    return MessageResponse(message="Event edited successfully") 
@app.get("/myevents", response_model =ListResponse)
async def my_events(request:Request) -> ListResponse:
    return ListResponse()