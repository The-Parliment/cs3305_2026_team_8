
from ..db.db import get_db
from ..db.structures.structures import User, Request, RequestTypes, Status
from sqlalchemy import select
import json

'''
    Common functions to do with Users
'''
def user_follows(user1, user2):
    db = get_db()
    stmt = select(Request).filter_by(field1=user1, field2=user2, 
                                         type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    result = db.scalar(stmt)
    return result is not None

def users_are_friends(user1, user2):
    db = get_db()
    stmt1 = select(Request).filter_by(field1=user1, field2=user2, 
                                          type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    stmt2 = select(Request).filter_by(field1=user2, field2=user1, 
                                          type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
    result1 = db.scalar(stmt1)
    result2 = db.scalar(stmt2)
    return result1 and result2

def user_following(user):
    db = get_db()
    result = select(Request.field2).filter_by(field1=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    return db.scalars(result).all()

'''Outgoing'''
def user_follow_requests(user):
    db = get_db()
    result = select(Request.field2).filter_by(field1=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    return db.scalars(result).all()

def user_followers(user):
    db = get_db()
    result = select(Request.field1).filter_by(field2=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED)
    return db.scalars(result).all()

'''Incoming'''
def user_follower_requests(user):
    db = get_db()
    result = select(Request.field1).filter_by(field2=user, 
                                                type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING)
    return db.scalars(result).all()

def user_friends(user):
    u_f = user_following(user)
    db = get_db()
    friends = []
    for u in u_f:
        stmt = select(Request).filter_by(field1=u, field2=user, 
                                             type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED).limit(1)
        result = db.scalar(stmt)
        if result:
            friends.append(u)
    return friends