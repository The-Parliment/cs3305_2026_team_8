import logging
from fastapi import Depends, Request
from fastapi import FastAPI, HTTPException
from sqlalchemy import delete, insert, select, update
from common.JWTSecurity import decode_and_verify
from common.db.structures.structures import Group as DBGroup, RequestTypes, Status, UserRequest
from common.db.db import get_db
from models import GroupCreate, Group, GroupInfoResponse, GroupsList, InviteResponse, ListInviteResponse, MessageResponse, GroupMembersList, GroupMemberInfo

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
async def create_group(new_group: GroupCreate, authorized_user: str = Depends(get_username_from_request)):
    logger.info(f"create_group called: {new_group}")
    if group_name_exists(new_group.group_name):
        raise HTTPException(status_code=400, detail="Group name already exists")
    with get_db() as db:
        db_group = DBGroup(
            group_name=new_group.group_name,
            group_desc=new_group.group_desc,
            is_private=new_group.is_private,
            owner=authorized_user
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return Group.model_validate(db_group)
    
@app.post("/edit/{group_id}", status_code=200, response_model=MessageResponse)
async def edit_group(group_id: int, updated_group: GroupCreate, authorized_user: str = Depends(get_username_from_request)):
    logger.info(f"edit_group called: {group_id} with data {updated_group}")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id and DBGroup.owner == authorized_user)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            return MessageResponse(message="Group does not exist or user is not the owner", valid=False)
        stmt2 = update(DBGroup).where(DBGroup.group_id == group_id).values(
            group_name=updated_group.group_name, 
            group_desc=updated_group.group_desc, 
            is_private=updated_group.is_private
            )
        db.execute(stmt2)
        db.commit()
        return MessageResponse(message="Group updated successfully")
    
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
        groups = []
        for group in result:
            groups.append(GroupInfoResponse(group_id=group.group_id, group_name=group.group_name, group_desc=group.group_desc, is_private=group.is_private, owner=group.owner))
        return GroupsList(group_list=groups)

@app.get("/mygroups", response_model=GroupsList)
async def my_groups(request: Request, authorized_user: str = Depends(get_username_from_request)):
    logger.info("my_groups called")
    with get_db() as db:
        stmt = select(DBGroup).join(UserRequest, DBGroup.group_id == UserRequest.field3).where(
            UserRequest.field2 == authorized_user,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.ACCEPTED
        )
        result = db.execute(stmt).scalars().all()
        groups = []
        for group in result:
            groups.append(GroupInfoResponse(group_id=group.group_id, group_name=group.group_name, group_desc=group.group_desc, is_private=group.is_private, owner=group.owner))
        stmt2 = select(DBGroup).where(DBGroup.owner == authorized_user)
        owned_groups = db.execute(stmt2).scalars().all()
        for group in owned_groups:
            if group not in groups:
                groups.append(GroupInfoResponse(group_id=group.group_id, group_name=group.group_name, group_desc=group.group_desc, is_private=group.is_private, owner=group.owner))
        return GroupsList(group_list=groups)

@app.get("/ismember/{group_id}/{user}", response_model=bool)
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
        stmt2 = select(DBGroup.owner).where(DBGroup.group_id == group_id)
        owner = db.execute(stmt2).scalar_one_or_none()
        if owner:
            group_member_list.append(GroupMemberInfo(username=owner))
        return GroupMembersList(members=group_member_list)

@app.get("/group_exists/{group_id}", response_model=bool)
async def this_group_exists(request:Request, group_id: int):
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
        print(f"DEBUG: Invite sent successfully to {user} for group {group_id}")
        return MessageResponse(message="Invite sent successfully")
    
@app.get("/group_info/{group_id}", response_model=GroupInfoResponse)
async def group_info(request: Request, group_id: int):
    logger.info(f"group_info called: {group_id}")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id)
        result = db.execute(stmt).scalar_one_or_none()
        if result:
            return GroupInfoResponse(group_id=result.group_id, group_name=result.group_name, group_desc=result.group_desc, is_private=result.is_private, owner=result.owner)
        else:
            return GroupInfoResponse(group_id=group_id, group_name="", group_desc="", is_private=False, owner="", valid=False)
    
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
        
@app.post("/remove/{group_id}/{user}", status_code=200, response_model=MessageResponse)
async def remove_member(request: Request, group_id: int, user: str, authorized_user: str = Depends(get_username_from_request)):
    logger.info("remove_member called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            return MessageResponse(message="Group does not exist", valid=False)
        if db_group.owner != authorized_user:
            return MessageResponse(message="Only the group owner can remove members", valid=False)
        if not is_user_in_group(user, group_id):
            return MessageResponse(message="User is not a member of the group", valid=False)
        stmt2 = delete(UserRequest).where(
            UserRequest.field2 == user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE
        )
        db.execute(stmt2)
        db.commit()
        return MessageResponse(message="User removed from group successfully")
    
@app.post("/accept_request/{group_id}/{user}", status_code=200, response_model=MessageResponse)
async def accept_request(request: Request, group_id: int, user: str, authorized_user: str = Depends(get_username_from_request)):
    logger.info("accept_request called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            return MessageResponse(message="Group does not exist", valid=False)
        if db_group.owner != authorized_user:
            return MessageResponse(message="Only the group owner can accept join requests", valid=False)
        if not is_user_requested_to_join_group(user, group_id):
            return MessageResponse(message="No pending join request from this user for this group", valid=False)
        stmt2 = update(UserRequest).values(status=Status.ACCEPTED).where(
            UserRequest.field1 == user,
            UserRequest.field2 == user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        db.execute(stmt2)
        db.commit()
        return MessageResponse(message="Join request accepted successfully")
    
@app.post("/decline_request/{group_id}/{user}", status_code=200, response_model=MessageResponse)
async def decline_request(request: Request, group_id: int, user: str, authorized_user: str = Depends(get_username_from_request)):
    logger.info("decline_request called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            return MessageResponse(message="Group does not exist", valid=False)
        if db_group.owner != authorized_user:
            return MessageResponse(message="Only the group owner can decline join requests", valid=False)
        if not is_user_requested_to_join_group(user, group_id):
            return MessageResponse(message="No pending join request from this user for this group", valid=False)
        stmt2 = delete(UserRequest).where(
            UserRequest.field1 == user,
            UserRequest.field2 == user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        db.execute(stmt2)
        db.commit()
        return MessageResponse(message="Join request declined successfully")
    
@app.post("/accept_invite/{group_id}", status_code=200, response_model=MessageResponse)
async def accept_invite(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("accept_invite called")
    with get_db() as db:
        if not is_user_invited_to_group(authorized_user, group_id):
            return MessageResponse(message="No pending invite for this user for this group", valid=False)
        stmt = update(UserRequest).values(status=Status.ACCEPTED).where(
            UserRequest.field1 != authorized_user,
            UserRequest.field2 == authorized_user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Invite accepted successfully")
    
@app.post("/decline_invite/{group_id}", status_code=200, response_model=MessageResponse)
async def decline_invite(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("decline_invite called")
    with get_db() as db:
        if not is_user_invited_to_group(authorized_user, group_id):
            return MessageResponse(message="No pending invite for this user for this group", valid=False)
        stmt = delete(UserRequest).where(
            UserRequest.field2 == authorized_user,
            UserRequest.field3 == group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE
        )
        db.execute(stmt)
        db.commit()
        return MessageResponse(message="Invite declined successfully")
    
@app.post("/join_public_group/{group_id}", status_code=200, response_model=MessageResponse)
async def join_public_group(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("join_public_group called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id)
        db_group = db.execute(stmt).scalar_one_or_none()
        if not db_group:
            print("Group does not exist")
            return MessageResponse(message="Group does not exist", valid=False)
        if is_user_invited_at_all(authorized_user, group_id):
            print("User has already been invited or has requested to join this group")
            return MessageResponse(message="You have already requested to join this group or are already a member", valid=False)
        if db_group.is_private:
            print("Group is private, must request to join instead")
            return MessageResponse(message="This group is private, you must request to join instead", valid=False)
        if is_user_in_group(authorized_user, group_id):
            print("User is already a member of this group")
            return MessageResponse(message="You are already a member of this group", valid=False)
        stmt2 = insert(UserRequest).values(
            field1=authorized_user,
            field2=authorized_user,
            field3=group_id,
            type=RequestTypes.GROUP_INVITE,
            status=Status.ACCEPTED
        )
        db.execute(stmt2)
        db.commit()
        print("Successfully joined the group")
        return MessageResponse(message="Successfully joined the group")
        
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
        print(f"DEBUG: Executing query to get invites for user {authorized_user}")
        result = db.execute(stmt).scalars().all()
        print(f"DEBUG: Found {len(result)} invites for user {authorized_user}")
        invite_list = []
        for req in result:
            group_stmt = select(DBGroup).where(DBGroup.group_id == req.field3)
            group_result = db.execute(group_stmt).scalar_one_or_none()
            if group_result:
                invite_list.append(InviteResponse(group_id=req.field3, group_name=group_result.group_name, username=req.field2))
            print(f"DEBUG: Found invite - Group ID: {req.field3}, Group Name: {group_result.group_name if group_result else 'Unknown'}, Invited By: {req.field1}")    
        return ListInviteResponse(invites=invite_list)

@app.get("/get_this_group_invites/{group_id}", response_model=ListInviteResponse)
async def get_this_group_invites(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("get_this_group_invites called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id, DBGroup.owner == authorized_user)
        group = db.execute(stmt).scalar_one_or_none()
        if not group:
            return ListInviteResponse(invites=[])
        req_stmt = select(UserRequest).where(
            UserRequest.field1 != UserRequest.field2,
            UserRequest.field3 == group.group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        result = db.execute(req_stmt).scalars().all()
        invite_list = []
        for req in result:
            invite_list.append(InviteResponse(group_id=req.field3, group_name=group.group_name, username=req.field2))
        return ListInviteResponse(invites=invite_list)
    
@app.get("/get_this_group_requests/{group_id}", response_model=ListInviteResponse)
async def get_this_group_requests(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("get_this_group_requests called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.group_id == group_id, DBGroup.owner == authorized_user)
        group = db.execute(stmt).scalar_one_or_none()
        if not group:
            return ListInviteResponse(invites=[])
        req_stmt = select(UserRequest).where(
            UserRequest.field1 == UserRequest.field2,
            UserRequest.field3 == group.group_id,
            UserRequest.type == RequestTypes.GROUP_INVITE,
            UserRequest.status == Status.PENDING
        )
        result = db.execute(req_stmt).scalars().all()
        request_list = []
        for req in result:
            request_list.append(InviteResponse(group_id=req.field3, group_name=group.group_name, username=req.field2))
        return ListInviteResponse(invites=request_list)
    
@app.get("/get_group_requests", response_model=ListInviteResponse)
async def get_group_requests(request: Request, authorized_user: str = Depends(get_username_from_request)):
    logger.info("get_group_requests called")
    with get_db() as db:
        stmt = select(DBGroup).where(DBGroup.owner == authorized_user)
        owned_groups = db.execute(stmt).scalars().all()
        request_list = []
        for group in owned_groups:
            req_stmt = select(UserRequest).where(
                UserRequest.field1 == UserRequest.field2,
                UserRequest.field3 == group.group_id,
                UserRequest.type == RequestTypes.GROUP_INVITE,
                UserRequest.status == Status.PENDING
            )
            result = db.execute(req_stmt).scalars().all()
            for req in result:
                request_list.append(InviteResponse(group_id=req.field3, group_name=group.group_name, username=req.field2))
        return ListInviteResponse(invites=request_list)
    
@app.get("/user_is_invited/{group_id}", response_model=bool)
async def user_is_invited(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("user_is_invited called")
    return is_user_invited_to_group(authorized_user, group_id)

@app.get("/user_is_requested/{group_id}", response_model=bool)
async def user_is_requested(request: Request, group_id: int, authorized_user: str = Depends(get_username_from_request)):
    logger.info("user_is_requested called")
    return is_user_requested_to_join_group(authorized_user, group_id)