
from common.JWTSecurity import decode_and_verify
from ..db.db import get_db
from ..db.structures.structures import User, UserDetails, UserRequest, RequestTypes, Status
from sqlalchemy import select, insert, delete, update
from fastapi import Request, HTTPException

'''
    Common functions to do with Users

'''

def get_user_claims(request: Request) -> dict:
    access = request.cookies.get("access_token")
    if not access:
        raise HTTPException(status_code=401)

    return decode_and_verify(token=access, expected_type="access")

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

def user_follows(user1, user2):
    db = get_db()
    stmt = select(UserRequest).filter_by(field1=user1, field2=user2, 
                                         type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    result = db.scalar(stmt)
    return result is not None

def users_are_friends(user1, user2):
    db = get_db()
    stmt1 = select(UserRequest).filter_by(field1=user1, field2=user2, 
                                          type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    stmt2 = select(UserRequest).filter_by(field1=user2, field2=user1, 
                                          type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    result1 = db.scalar(stmt1)
    result2 = db.scalar(stmt2)
    return result1 and result2

def user_following(user):
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    return db.scalars(result).all()

'''Outgoing'''
def user_follow_requests(user):
    db = get_db()
    result = select(UserRequest.field2).filter_by(field1=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    return db.scalars(result).all()

def user_followers(user):
    db = get_db()
    result = select(UserRequest.field1).filter_by(field2=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    return db.scalars(result).all()

'''Incoming'''
def user_follower_requests(user):
    db = get_db()
    result = select(UserRequest.field1).filter_by(field2=user, 
                                                type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    return db.scalars(result).all()

def user_friends(user):
    u_f = user_following(user)
    db = get_db()
    friends = []
    for u in u_f:
        stmt = select(UserRequest).filter_by(field1=u, field2=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
        result = db.scalar(stmt)
        if result:
            friends.append(u)
    return friends