import logging
import os
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from httpcore import request
from common.clients.client import get
from events_model import CreateRequest, InfoResponse, ListEventResponse, MessageResponse, ListResponse, InviteRequest, CancelRequest, EditRequest
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, Venue, UserRequest, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from events_database import event_exists, is_user_attending, is_user_invited
from sqlalchemy import select, insert, delete, update

logging.basicConfig(level=logging.INFO, format='[events] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/events", title="events_service")
CIRCLES_INTERNAL_BASE = os.getenv("CIRCLES_INTERNAL_BASE", "http://circles:8002")

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
async def create_event(inbound: CreateRequest) -> MessageResponse:
    db = get_db()
    stmt= insert(Events).values(
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

@app.get("/eventinfo/{event_id}", response_model=InfoResponse)
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
async def invite_user(inbound: InviteRequest, username:int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    stmt = insert(UserRequest).values(
        field1=authorized_user,
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

@app.post("/invitecircle/{event_id}", response_model=MessageResponse)
async def invite_circle(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    circle_members_data = await get(CIRCLES_INTERNAL_BASE, "mycircle", 
                               headers={"Cookie" : f"access_token={inbound.cookies.get('access_token')}"})
    circle_members = circle_members_data.get("user_names", [])
    for member in circle_members:
        stmt = insert(UserRequest).values(
            field1=authorized_user,
            field2=member,
            field3=event_id,
            type=RequestTypes.EVENT_INVITE,
            status=Status.PENDING
        )
        db.execute(stmt)
    db.commit()
    return MessageResponse(message=f"Invited your circle to this event!")


#cannot complete group code without darrens code
@app.post("/invitegroup", response_model=MessageResponse)
async def invite_group(inbound: InviteRequest) -> MessageResponse:
    invite_group_response = MessageResponse( 
        message="foodwise wuz here",
        )
    return invite_group_response 

@app.post("/cancel/{event_id}", response_model=MessageResponse)
async def cancel_event(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    if not event_exists(event_id):
        return MessageResponse(message="There is no such event")
    stmt=delete(Events).where(
        id=event_id,
        host=authorized_user
    )
    db.execute(stmt)
    db.commit()
    return MessageResponse(message="Event cancelled successfully.")

@app.put("/edit", response_model=MessageResponse)
async def edit_event(inbound: EditRequest) -> MessageResponse:
    edit_event_response = MessageResponse( 
        event_id=inbound.event_id,
        title=inbound.title,
        description=inbound.description,
        datetime_start=inbound.datetime_start,
        datetime_end=inbound.datetime_end,
        latitude=inbound.latitude,
        longitude=inbound.longitude,
        venue_id=inbound.venue_id)
    return edit_event_response

@app.post("/attend/{event_id}", response_model=MessageResponse)
async def attend_event(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    if not event_exists(event_id):
        return MessageResponse(message="There is no such event")
    if is_user_invited(event_id, authorized_user):
        stmt = update(UserRequest).values(
            status=Status.ACCEPTED
        ).where(
            field2=authorized_user,
            field3=event_id,
            type=RequestTypes.EVENT_INVITE
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Invitation accepted, you are now attending the event!")
    else:
        stmt=insert(UserRequest).values(
            field1=event_id,
            field2=authorized_user,
            field3=event_id,
            type=RequestTypes.EVENT_INVITE,
            status=Status.ACCEPTED
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="You are now attending the event!")
    
@app.post("/decline/{event_id}", response_model=MessageResponse)
async def decline_event(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    db = get_db()
    if not event_exists(event_id):
        return MessageResponse(message="There is no such event")
    if is_user_invited(event_id, authorized_user):
        stmt = delete(UserRequest).where(
            field2=authorized_user,
            field3=event_id,
            type=RequestTypes.EVENT_INVITE
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Invitation declined, you are not attending the event.")
    else:
        return MessageResponse(message="You were not invited to this event, so you cannot decline it. If you do not wish to attend, simply ignore the invitation.")

@app.get("/myevents", response_model=ListEventResponse)
async def my_events(request:Request, authorized_user=Depends(get_username_from_request)) -> ListEventResponse:
    db = get_db()
    stmt = select(UserRequest.field3).filter_by(
        field2=authorized_user,
        type=RequestTypes.EVENT_INVITE,
        status=Status.ACCEPTED
    )
    events = db.scalars(stmt).all()
    list_of_events = []
    for event_id in events:
        stmt = select(Events).filter_by(id=event_id)
        event = db.scalars(stmt).first()
        if event:
            list_of_events.append(InfoResponse(id=event.id,
                            venue=event.venue,
                            latitude=event.latitude,
                            longitude=event.longitude,
                            datetime_start=event.datetime_start,
                            datetime_end=event.datetime_end,
                            title=event.title,
                            description=event.description,
                            host=event.host))
    return ListEventResponse(list=list_of_events)

@app.get("/all_events", response_model=ListEventResponse)
async def all_events(request:Request) -> ListEventResponse:
    db = get_db()
    stmt = select(Events)
    result = db.execute(stmt).scalars().all()
    if not result: 
        return ListEventResponse(list=[])
    list_of_events = []
    for event in result:
        list_of_events.append(InfoResponse(id=event.id,
                        venue=event.venue,
                        latitude=event.latitude,
                        longitude=event.longitude,
                        datetime_start=event.datetime_start,
                        datetime_end=event.datetime_end,
                        title=event.title,
                        description=event.description,
                        host=event.host))
        
    response = ListEventResponse(events=list_of_events)
    return response

@app.get("/get_attendees/{event_id}", response_model=ListResponse)
async def get_attendees(event_id: int) -> ListResponse:
    db = get_db()
    stmt = select(UserRequest.field2).filter_by(
        field3=event_id,
        type=RequestTypes.EVENT_INVITE,
        status=Status.ACCEPTED
    )
    attendees = db.scalars(stmt).all()
    return ListResponse(lst=attendees)