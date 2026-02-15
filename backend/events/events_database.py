from common.db.db import get_db
from common.db.structures.structures import Events, Request, RequestTypes, Status
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

