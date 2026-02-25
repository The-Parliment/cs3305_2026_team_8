# You could ignore this file and put the content in main.py
# but often its nice to seperate.
# this file just contains the class definitions for your pydantic models
# Basically what a  client calls the endoint.
# Likely a CreateGroup here....

import datetime
import logging
from pydantic import BaseModel, ConfigDict

# Class defs here

class GroupCreate(BaseModel):
    group_name: str
    group_desc: str
    is_private: bool
    owner: str

# Completed class mimicing HTTP response parameters.
# Using inheritance to take advantage of the class above and adding group_id
# group_id = db's Primary Key
class Group(GroupCreate):
    group_id: int
    model_config = ConfigDict(from_attributes=True)


class GroupsList(BaseModel):
    group_list: list[Group]
    model_config = ConfigDict(from_attributes=True)

class GroupJoin(BaseModel):
    username: str
    group_id: int

# Setting leave up with username first to make easier
class GroupLeave(BaseModel):
    username: str
    group_id: int

class GroupsMine(BaseModel):
    username: str

class GroupIsMember(BaseModel):
    username: str
    group_id: int

class GroupMemberInfo(BaseModel):
    username: str
    model_config = ConfigDict(from_attributes=True)

class GroupMembersList(BaseModel):
    members: list[GroupMemberInfo]