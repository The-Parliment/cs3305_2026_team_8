import logging
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from models import *
import crud

logging.basicConfig(level=logging.INFO, format='[proximity] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from common.db.db import get_db
from common.db.init import init_db
from common.db.structures.structures import Group  # Import the Group model

app = FastAPI(root_path="/groups", title="groups_service")

# Pydantic models inbound request 
# class GroupCreate(BaseModel):

@app.on_event("startup")
def startup_groups():
    """Initialize database tables on Groups startup"""
    init_db()

@app.get("/")
async def root():
    return {"Groups Service: API called"}

@app.post("/create")
async def create_group(new_group: GroupCreate, db_handle: Session = Depends(get_db)):
    group_id = crud.create_group(db_handle, new_group)
    return group_id
