import logging
from datetime import datetime
from fastapi import Request
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from common.db.structures.structures import Group as DBGroup, GroupMembers
from common.db.db import get_db
from models import GroupCreate, Group, GroupsList, GroupJoin, GroupLeave, GroupsMine, GroupIsMember, GroupMembersList, GroupMemberInfo

logging.basicConfig(level=logging.INFO, format='[groups] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/groups", title="groups_service")

@app.get("/")
async def root():
    return {"message": "Groups Service: API called"}

@app.post("/create", response_model=Group, status_code=201)
async def create_group(new_group: GroupCreate):
    logger.info(f"create_group called: {new_group}")
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

@app.post("/join", status_code=200)
async def join_group(join_handle: GroupJoin):
    logger.info(f"join_group called: {join_handle}")
    with get_db() as db:
        try:
            db_join = GroupMembers(
                group_id=join_handle.group_id,
                username=join_handle.username,
                date_joined=datetime.utcnow()
            )
            db.add(db_join)
            db.commit()
            return {"message": "Successfully joined group"}
        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError: {e}")
            raise HTTPException(status_code=409, detail="Failed to join group")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {e}")
            raise

@app.get("/list", response_model=GroupsList)
async def list_all_groups(request:Request):
    logger.info("list_all_groups called")
    with get_db() as db:
        result = db.execute(select(DBGroup)).scalars().all()
        print(f"RAW RESULT: {result}")
        print(f"COUNT: {len(result)}")
        return GroupsList(group_list=result)

@app.post("/leave", status_code=200)
async def leave_group(leave_handle: GroupLeave):
    logger.info("leave_group called")
    with get_db() as db:
        try:
            db_member = db.execute(
                select(GroupMembers).where(
                    GroupMembers.group_id == leave_handle.group_id,
                    GroupMembers.username == leave_handle.username
                )
            ).scalar_one_or_none()

            if db_member is None:
                return {"message": "Successfully left group"}

            db.delete(db_member)
            db.commit()
            return {"message": "Successfully left group"}
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error: {e}")
            raise

@app.post("/mygroups", response_model=GroupsList)
async def my_groups(my_groups_handle: GroupsMine):
    logger.info("my_groups called")
    with get_db() as db:
        result = db.execute(
            select(DBGroup)
            .join(GroupMembers, DBGroup.group_id == GroupMembers.group_id)
            .where(GroupMembers.username == my_groups_handle.username)
        ).scalars().all()
        return GroupsList(group_list=result)

@app.post("/ismember", response_model=bool)
async def is_member(is_member_handle: GroupIsMember):
    logger.info(f"is_member called: {is_member_handle}")
    with get_db() as db:
        result = db.execute(
            select(GroupMembers).where(
                GroupMembers.group_id == is_member_handle.group_id,
                GroupMembers.username == is_member_handle.username
            )
        ).scalar_one_or_none()
        return result is not None

@app.get("/listmembers/{group_id}", response_model=GroupMembersList)
async def list_members(group_id: int):
    logger.info(f"list_members called: {group_id}")
    with get_db() as db:
        result = db.execute(
            select(GroupMembers).where(GroupMembers.group_id == group_id)
        ).scalars().all()
        return GroupMembersList(members=[GroupMemberInfo(username=m.username) for m in result])

@app.get("/group_exists/{group_id}", response_model=bool)
async def group_exists(group_id: int):
    logger.info(f"group_exists called: {group_id}")
    with get_db() as db:
        result = db.execute(
            select(DBGroup).where(DBGroup.group_id == group_id)
        ).scalar_one_or_none()
        return result is not None