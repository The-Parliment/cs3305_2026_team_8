import logging
from fastapi import Depends, Request
from fastapi import FastAPI, HTTPException
from sqlalchemy import delete, insert, select
from backend.events.events_model import InviteResponse, ListInviteResponse
from common.JWTSecurity import decode_and_verify
from common.db.structures.structures import Group as DBGroup, RequestTypes, Status, UserRequest
from common.db.db import get_db
from models import GroupCreate, Group, GroupsList, MessageResponse, GroupMembersList, GroupMemberInfo

logging.basicConfig(level=logging.INFO, format='[groups] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/groups", title="groups_service")

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
        
def is_user_in_group(username: str, group_id: int) -> bool:
    with get_db() as db:
        stmt = select(UserRequest).where(
            UserRequest.field2 == username,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.ACCEPTED
        )
        result = db.execute(stmt).scalar_one_or_none()
        return result is not None

def is_user_invited_to_group(username: str, group_id: int) -> bool:
    with get_db() as db:
        result = db.execute(
            select(UserRequest).where(
                UserRequest.field1 != username,
                UserRequest.field2 == username,
                UserRequest.field3 == group_id,
                UserRequest.type == RequestTypes.GROUP_INVITE,
                UserRequest.status == Status.PENDING
            )
        ).scalar_one_or_none()
        return result is not None

def is_user_requested_to_join_group(username: str, group_id: int) -> bool:
    with get_db() as db:
        result = db.execute(
            select(UserRequest).where(
                UserRequest.field1 == username,
                UserRequest.field2 == username,
                UserRequest.field3 == group_id,
                UserRequest.type == RequestTypes.GROUP_INVITE,
                UserRequest.status == Status.PENDING
            )
        ).scalar_one_or_none()
        return result is not None
def is_user_invited_at_all(username: str, group_id: int) -> bool:
    return is_user_invited_to_group(username, group_id) or is_user_requested_to_join_group(username, group_id)
    
def group_exists(group_id: int) -> bool:
    with get_db() as db:
        result = db.execute(
            select(DBGroup).where(DBGroup.group_id == group_id)
        ).scalar_one_or_none()
        return result is not None
    
def group_name_exists(group_name: str) -> bool:
    with get_db() as db:
        result = db.execute(
            select(DBGroup).where(DBGroup.group_name == group_name)
        ).scalar_one_or_none()
        return result is not None

@app.get("/")
async def root():
    return {"message": "Groups Service: API called"}

@app.post("/create", response_model=Group, status_code=201)
async def create_group(new_group: GroupCreate):
    logger.info(f"create_group called: {new_group}")
    if group_name_exists(new_group.group_name):
        raise HTTPException(status_code=400, detail="Group name already exists")
    with get_db() as db:
        db_group = DBGroup(
            group_name=new_group.group_name,
            group_desc=new_group.group_desc,
            is_private=new_group.is_private,
            owner=new_group.owner
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return Group.model_validate(db_group)
    
@app.post("/delete/{group_id}", status_code=200, response_model=MessageResponse)
async def delete_group(group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info(f"delete_group called: {group_id}")
    with get_db() as db:
        if not group_exists(group_id):
            return MessageResponse(message="Group does not exist", valid=False)
        stmt = select(DBGroup).where(DBGroup.group_id == group_id and DBGroup.owner == authorized_user)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            return MessageResponse(message="Group does not exist or user is not the owner", valid=False)
        db.delete(db_group)
        stmt2 = select(UserRequest).where(
            UserRequest.field3 == group_id
        )
        result = db.execute(stmt2).scalars().all()
        for req in result:
            db.delete(req)
        db.commit()
        return MessageResponse(message="Group deleted successfully")

@app.get("/list", response_model=GroupsList)
async def list_all_groups(request:Request):
    logger.info("list_all_groups called")
    with get_db() as db:
        result = db.execute(select(DBGroup)).scalars().all()
        print(f"RAW RESULT: {result}")
        print(f"COUNT: {len(result)}")
        return GroupsList(group_list=result)

@app.post("/mygroups", response_model=GroupsList)
async def my_groups(request: Request, authorized_user: str = Depends(get_username_from_request)):
    logger.info("my_groups called")
    with get_db() as db:
        stmt = select(DBGroup.group_id).join(UserRequest, DBGroup.group_id == UserRequest.field3).where(
            UserRequest.field2 == authorized_user,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.ACCEPTED
        )
        result = db.execute(stmt).scalars().all()
        return GroupsList(group_list=result)

@app.post("/ismember/{group_id}/{user}", response_model=bool)
async def is_member(request: Request, group_id: int, user: str):
    logger.info(f"is_member called: {request}")
    return is_user_in_group(user, group_id)

@app.get("/listmembers/{group_id}", response_model=GroupMembersList)
async def list_members(request:Request, group_id: int):
    logger.info(f"list_members called: {group_id}")
    with get_db() as db:
        stmt = select(UserRequest).where(
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.ACCEPTED
        )
        result = db.execute(stmt).scalars().all()
        group_member_list = []
        for req in result:
            group_member_list.append(GroupMemberInfo(username=req.field2))
        return GroupMembersList(members=group_member_list)

@app.get("/group_exists/{group_id}", response_model=bool)
async def group_exists(request:Request, group_id: int):
    logger.info(f"group_exists called: {group_id}")
    return group_exists(group_id)
    
@app.post("/invite/{user}/{group_id}", status_code=200, response_model=MessageResponse)
async def invite_to_group(request: Request, user: str, group_id: int, authorized_user:str = Depends(get_username_from_request)):
    if is_user_invited_at_all(user, group_id):
        return MessageResponse(message="User has already been invited or has requested to join this group", valid=False)
    with get_db() as db:
        stmt = insert(UserRequest).values(
            field1=authorized_user,
            field2=user,
            field3=group_id,
            type=RequestTypes.GROUP_INVITE,
            status=Status.PENDING
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Invite sent successfully")
    
@app.post("/request/{group_id}", status_code=200, response_model=MessageResponse)
async def join_group(request: Request, group_id: int, authorized_user:str = Depends(get_username_from_request)):
    logger.info(f"join_group called: {group_id}")
    if is_user_invited_at_all(authorized_user, group_id):
            return MessageResponse(message="You have already requested to join this group or are already a member", valid=False)
    with get_db() as db:
        stmt = insert(UserRequest).values(
            field1=authorized_user,
            field2=authorized_user,
            field3=group_id,
            type=RequestTypes.GROUP_INVITE,
            status=Status.PENDING
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Join request sent successfully")
        
@app.post("/leave/{group_id}", status_code=200, response_model=MessageResponse)
async def leave_group(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("leave_group called")
    with get_db() as db:
        if not is_user_in_group(authorized_user, group_id):
            return MessageResponse(message="User is not a member of the group", valid=False)
        stmt = select(UserRequest).where(
            UserRequest.field2 == authorized_user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.ACCEPTED
        )
        result = db.execute(stmt).scalar_one_or_none()
        if result:
            stmt2 = delete(UserRequest).where(
                UserRequest.field2 == authorized_user,
                UserRequest.field3 == group_id,
                UserRequest.type == RequestTypes.GROUP_INVITE
            )
            db.execute(stmt2)
            db.commit()
            return MessageResponse(message="Successfully left the group")
        else:
            return MessageResponse(message="User is not a member of the group")
        
@app.get("/get_group_invites", response_model=ListInviteResponse)
async def get_group_invites(request: Request, authorized_user: str = Depends(get_username_from_request)):
    logger.info("get_group_invites called")
    with get_db() as db:
        stmt = select(UserRequest).where(
            UserRequest.field1 != authorized_user,
            UserRequest.field2 == authorized_user,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        result = db.execute(stmt).scalars().all()
        invite_list = []
        for req in result:
            group_stmt = select(DBGroup).where(DBGroup.group_id == req.field3)
            group_result = db.execute(group_stmt).scalar_one_or_none()
            if group_result:
                invite_list.append(InviteResponse(group_id=req.field3, group_name=group_result.group_name, username=req.field2))
        return ListInviteResponse(invites=invite_list)
    
@app.get("/get_group_requests", response_model=ListInviteResponse)
async def get_group_requests(request: Request, authorized_user: str = Depends(get_username_from_request)):
    logger.info("get_group_requests called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.owner == authorized_user)
        owned_groups = db.execute(stmt).scalars().all()
        request_list = []
        for group in owned_groups:
            req_stmt = select(UserRequest).where(
                UserRequest.field1 != UserRequest.field2,
                UserRequest.field3 == group.group_id,
                UserRequest.type == RequestTypes.GROUP_INVITE,
                UserRequest.status == Status.PENDING
            )
            result = db.execute(req_stmt).scalars().all()
            for req in result:
                request_list.append(InviteResponse(group_id=req.field3, group_name=group.group_name, username=req.field2))