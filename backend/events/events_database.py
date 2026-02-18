from common.db.db import get_db
from common.db.structures.structures import Events, UserRequest, RequestTypes, Status
from sqlalchemy import select, insert, delete, update
import json

'''
    Common functions to do with Events

'''

def event_exists(event):
    db = get_db()
    stmt = select(Events).filter_by(event_id=event).limit(1)
    result = db.scalar(stmt)
    return result is not None


def event_is_public(event):
    db = get_db()
    stmt = select(Events).filter_by(event_id=event).limit(1)
    result = db.scalar(stmt)
    if result is not None:
        return result.public
    return False

def is_user_invited(event, user):
    db = get_db()
    stmt = select(UserRequest).filter_by(field2=user, field3=event, type=RequestTypes.EVENT_INVITE).limit(1)
    result = db.scalar(stmt)
    if result is not None:
        return True
    return False

def is_user_attending(event, user):
    db = get_db()
    stmt = select(UserRequest).filter_by(field2=user, field3=event, type=RequestTypes.EVENT_INVITE, status=Status.ACCEPTED).limit(1)
    result = db.scalar(stmt)
    if result is not None:
        return True
    return False