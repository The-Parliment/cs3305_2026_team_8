
from common.JWTSecurity import decode_and_verify
from ..db.db import get_db
from ..db.structures.structures import User, UserDetails, UserRequest, RequestTypes, Status
from sqlalchemy import select, insert, delete, update
from fastapi import Request, HTTPException
from pydantic import BaseModel

'''
    Common functions to do with Users

'''

def user_exists(user):
    db = get_db()
    stmt = select(User).filter_by(username=user).limit(1)
    result = db.scalar(stmt)
    return result is not None

def email_exists(email):
    db = get_db()
    stmt = select(UserDetails).filter_by(email=email).limit(1)
    result = db.scalar(stmt)
    return result is not None

def phone_number_exists(phone_number):
    db = get_db()
    stmt = select(UserDetails).filter_by(phone_number=phone_number).limit(1)
    result = db.scalar(stmt)
    return result is not None