import logging
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from models import *
import crud

logging.basicConfig(level=logging.INFO, format='[proximity] %(asctime)s%(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from schema import DBGroup
from db import SessionLocal

app = FastAPI(root_path="/groups", title="groups_service")

# Pydantic models inbound request 
# class GroupCreate(BaseModel):

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"Groups Service: API called"}

@app.post("/create")
async def create_group(new_group: GroupCreate, db_handle: Session = Depends(get_db)):
    group_id = crud.create_group(db_handle, new_group)
    return group_id
