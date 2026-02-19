import logging
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from common.clients.client import get
from events_model import BooleanResponse, CreateRequest, CreateResponse, InfoResponse, ListEventResponse, ListInviteResponse, InviteResponse, MessageResponse, ListResponse, InviteRequest, EditRequest
from common.JWTSecurity import decode_and_verify                    # Importing cillians Security libs.
from common.db.structures.structures import Events, UserRequest, RequestTypes, Status    # Importing cillians DB models.
from common.db.db import get_db
from events_database import event_exists, event_is_public, is_requested, is_user_attending_event, is_user_invited_event, is_user_invited_event_pending, user_is_host
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

@app.post("/create", response_model=CreateResponse)
async def create_event(inbound: CreateRequest, authorized_user=Depends(get_username_from_request)) -> CreateResponse:
    print(f"Creating event with title: {inbound.title}, host: {authorized_user}")
    with get_db() as db:
        event = Events(
            title=inbound.title,
            venue=inbound.venue,
            datetime_start=inbound.datetime_start,
            datetime_end=inbound.datetime_end,
            latitude=inbound.latitude,
            longitude=inbound.longitude,
            description=inbound.description,
            host=authorized_user,
            public=inbound.public
        )
        db.add(event)
        print("Event added to session, committing...")
        db.flush()  # Ensure the new event ID is generated
        db.commit()
        db.refresh(event)  # Refresh the event instance to get the generated ID
        print(f"Event committed with ID: {event.id}")
        return CreateResponse(event_id=event.id)

@app.get("/eventinfo/{event_id}", response_model=InfoResponse)
async def event_info(request: Request, event_id:int):
    with get_db() as db:
        result=select(Events).filter_by(id=event_id).limit(1)
        event=db.scalar(result)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return InfoResponse(id=event.id, 
                            venue=event.venue, 
                            latitude=event.latitude, 
                            longitude=event.longitude,
                            datetime_start=event.datetime_start, 
                            datetime_end=event.datetime_end, 
                            title=event.title, 
                            description=event.description, 
                            host=event.host,
                            public=event.public
                            )

# too complicated to fill out with rest of them
@app.get("/search", response_model = ListResponse)
async def search_events(request:Request) -> ListResponse:
    with get_db() as db:
        result=select(Events).filter_by
        return ListResponse() # needs to be filled out + restructured for scaling

@app.post("/invite/{username}", response_model=MessageResponse)
async def invite_user(inbound: InviteRequest, username:int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
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
    with get_db() as db:
        circle_members_data = await get(CIRCLES_INTERNAL_BASE, "mycircle", 
                                   headers={"Cookie" : f"access_token={inbound.cookies.get('access_token')}"})
        circle_members = circle_members_data.get("user_names", [])
        print(f"Inviting circle members: {circle_members} to event {event_id}")
        for member in circle_members:
            stmt = select(UserRequest).filter_by(
                field2=member,
                field3=event_id,
                type=RequestTypes.EVENT_INVITE
            )
            result = db.scalars(stmt).all()
            if not result:
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
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="There is no such event")
        stmt=delete(Events).filter_by(
            id=event_id,
            host=authorized_user
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Event cancelled successfully.")

@app.post("/edit/{event_id}", response_model=MessageResponse)
async def edit_event(inbound: EditRequest, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="Event not found", valid=False)
        if not user_is_host(event_id, authorized_user):
            return MessageResponse(message="You are not the host of this event", valid=False)
        stmt = update(Events).filter_by(id=event_id).values(
            title=inbound.title,
            description=inbound.description,
            datetime_start=inbound.datetime_start,
            datetime_end=inbound.datetime_end,
            latitude=inbound.latitude,
            longitude=inbound.longitude,
            venue=inbound.venue,
            public=inbound.public
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Event updated successfully")

@app.post("/attend/{event_id}", response_model=MessageResponse)
async def attend_event(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="There is no such event")
        if is_user_invited_event(event_id, authorized_user):
            stmt = update(UserRequest).values(
                status=Status.ACCEPTED
            ).filter_by(
                field2=authorized_user,
                field3=event_id,
                type=RequestTypes.EVENT_INVITE
            )
            db.execute(stmt)
            db.commit()
            return MessageResponse(message="Invitation accepted, you are now attending the event!")
        else:
            return MessageResponse(message="You were not invited to this event, so you cannot accept it. If you wish to attend, please request to attend the event and wait for the host to accept your request.")
    
@app.post("/decline/{event_id}", response_model=MessageResponse)
async def decline_event(inbound: Request, event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="There is no such event")
        if is_user_invited_event(event_id, authorized_user):
            stmt = delete(UserRequest).filter_by(
                field2=authorized_user,
                field3=event_id,
                type=RequestTypes.EVENT_INVITE
            )
            db.execute(stmt)
            db.commit()
            return MessageResponse(message="Invitation declined, you are not attending the event.")
        else:
            if is_requested(event_id, authorized_user):
                stmt = delete(UserRequest).filter_by(
                    field1=authorized_user,
                    field2=authorized_user,
                    field3=event_id,
                    type=RequestTypes.EVENT_INVITE
                )
                db.execute(stmt)
                db.commit()
                return MessageResponse(message="Your request to attend the event has been withdrawn.")
            return MessageResponse(message="You were not invited to this event, so you cannot decline it. If you do not wish to attend, simply ignore the invitation.")

@app.post("/accept/{event_id}/{username}", response_model=MessageResponse)
async def accept_event(inbound: Request, event_id: int, username: str, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="There is no such event")
        if not user_is_host(event_id, authorized_user):
            return MessageResponse(message="You are not the host of this event, so you cannot accept invitations to this event.")
        if is_requested(event_id, username):
            stmt = update(UserRequest).values(
                status=Status.ACCEPTED
            ).filter_by(
                field1=username,
                field2=username,
                field3=event_id,
                type=RequestTypes.EVENT_INVITE
            )
            db.execute(stmt)
            db.commit()
            return MessageResponse(message="Invitation accepted, you are now attending the event!")
        else:
            return MessageResponse(message="You were not invited to this event, so you cannot accept it.")

@app.get("/myevents", response_model=ListEventResponse)
async def my_events(request:Request, authorized_user=Depends(get_username_from_request)) -> ListEventResponse:
    with get_db() as db:
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
                                host=event.host,
                                public=event.public
                                ))
        return ListEventResponse(list=list_of_events)
    
@app.post("/request/{event_id}", response_model=MessageResponse)
async def request_to_attend_event(event_id: int, authorized_user=Depends(get_username_from_request)) -> MessageResponse:
    with get_db() as db:
        if not event_exists(event_id):
            return MessageResponse(message="There is no such event")
        if event_is_public(event_id):
            return MessageResponse(message="This event is public, so you cannot request to attend it. Please join directly.")
        stmt=insert(UserRequest).values(
            field1=authorized_user,
            field2=authorized_user,
            field3=event_id,
            type=RequestTypes.EVENT_INVITE,
            status=Status.PENDING
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Your request to attend the event has been sent.")

@app.get("/my_invites", response_model=ListEventResponse)
async def my_invites(request:Request, authorized_user=Depends(get_username_from_request)) -> ListEventResponse:
    with get_db() as db:
        stmt = select(UserRequest.field3).filter(UserRequest.field1 != authorized_user,
                                                UserRequest.field2 == authorized_user,
                                                UserRequest.type == RequestTypes.EVENT_INVITE,
                                                UserRequest.status == Status.PENDING)
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
                                host=event.host,
                                public=event.public
                                ))
        return ListEventResponse(events=list_of_events)

@app.get("/all_events", response_model=ListEventResponse)
async def all_events(request:Request) -> ListEventResponse:
    with get_db() as db:
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
                            host=event.host,
                            public=event.public))
            
        response = ListEventResponse(events=list_of_events)
        return response

@app.get("/get_attendees/{event_id}", response_model=ListResponse)
async def get_attendees(event_id: int) -> ListResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    with get_db() as db:
        stmt = select(UserRequest.field2).filter_by(
            field3=event_id,
            type=RequestTypes.EVENT_INVITE,
            status=Status.ACCEPTED
        )
        attendees = db.scalars(stmt).all()
        return ListResponse(lst=attendees)

@app.get("/is_attending/{event_id}/{username}", response_model=BooleanResponse)
async def is_user_attending(request:Request, event_id: int, username: str) -> BooleanResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    if is_user_attending_event(event_id, username):
        return BooleanResponse(value=True)
    else:
        return BooleanResponse(value=False)
    
@app.get("/is_invited/{event_id}/{username}", response_model=BooleanResponse)
async def is_user_invited(request:Request, event_id: int, username: str) -> BooleanResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    if is_user_invited_event(event_id, username):
        return BooleanResponse(value=True)
    else:
        return BooleanResponse(value=False)
    
@app.get("/is_invited_pending/{event_id}/{username}", response_model=BooleanResponse)
async def is_user_invited_pending(request:Request, event_id: int, username: str) -> BooleanResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    if is_user_invited_event_pending(event_id, username):
        return BooleanResponse(value=True)
    else:
        return BooleanResponse(value=False)
    
@app.get("/is_host/{event_id}/{username}", response_model=BooleanResponse)
async def is_user_host(request:Request, event_id: int, username: str) -> BooleanResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    if user_is_host(event_id, username):
        return BooleanResponse(value=True)
    else:
        return BooleanResponse(value=False)

@app.get("/is_requested/{event_id}/{username}", response_model=BooleanResponse)
async def is_user_requested(request:Request, event_id: int, username: str) -> BooleanResponse:
    if not event_exists(event_id):
        return BooleanResponse(value=False)
    if is_requested(event_id, username):
        return BooleanResponse(value=True)
    else:
        return BooleanResponse(value=False)
    
@app.get("/my_pending_invites", response_model=ListInviteResponse)
async def my_pending_invites(request:Request, authorized_user=Depends(get_username_from_request)) -> ListInviteResponse:
    with get_db() as db:
        my_hosted_events_stmt = select(Events).filter_by(host=authorized_user)
        my_hosted_events = db.scalars(my_hosted_events_stmt).all()
        pending_invites = []
        for event in my_hosted_events:
            if not event.public:
                stmt = select(UserRequest).filter_by(
                    field3=event.id,
                    type=RequestTypes.EVENT_INVITE,
                    status=Status.PENDING
                )
                result = db.scalars(stmt).all()
                for invite in result:
                    if not is_requested(event.id, invite.field2):
                        continue
                    pending_invites.append(InviteResponse(
                        event_id=event.id,
                        username=invite.field2,
                        title=event.title
                    ))
        return ListInviteResponse(invites=pending_invites)