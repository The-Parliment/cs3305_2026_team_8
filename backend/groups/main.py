import logging
from fastapi import Request
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException
from models import GroupCreate, Group, GroupsList, GroupJoin, GroupLeave, GroupsMine, GroupIsMember, GroupMembersList

import crud

logging.basicConfig(level=logging.INFO, format='[groups] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/groups", title="groups_service")

@app.get("/")
async def root():
    return {"message": "Groups Service: API called"}

@app.post("/create", response_model=Group, status_code=201)
async def create_group(new_group: GroupCreate):
    logger.info(f"create_group called: {new_group}")
    return crud.create_group(new_group)

@app.post("/join", status_code=200)
async def join_group(join_handle: GroupJoin):
    logger.info(f"join_group called: {join_handle}")
    if not crud.db_join_group(join_handle):
        raise HTTPException(status_code=409, detail="Failed to join group")
    return {"message": "Successfully joined group"}

@app.get("/list", response_model=GroupsList)
async def list_all_groups(request:Request):
    logger.info("list_all_groups called")
    return crud.list_all_groups()

@app.post("/leave", status_code=200)
async def leave_group(leave_handle: GroupLeave):
    logger.info("leave_group called")
    crud.leave_group(leave_handle)
    return {"message": "Successfully left group"}

@app.post("/mygroups", response_model=GroupsList)
async def my_groups(my_groups_handle: GroupsMine):
    logger.info("my_groups called")
    return crud.my_groups(my_groups_handle)

@app.post("/ismember", response_model=bool)
async def is_member(is_member_handle: GroupIsMember):
    logger.info(f"is_member called: {is_member_handle}")
    return crud.is_member(is_member_handle.group_id, is_member_handle.username)

@app.get("/listmembers/{group_id}", response_model=GroupMembersList)
async def list_members(group_id: int):
    logger.info(f"list_members called: {group_id}")
    return crud.list_members(group_id)

@app.get("/group_exists/{group_id}", response_model=bool)
async def group_exists(group_id: int):
    logger.info(f"group_exists called: {group_id}")
    return crud.group_exists(group_id)