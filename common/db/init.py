from common.db.engine import engine
from common.db.base import Base
from common.db.structures.structures import User, UserRequest, RequestTypes, Status
from passlib.context import CryptContext
from .db import get_db
import common.db.structures

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    temp_remove_in_production()

def temp_remove_in_production():
    db = get_db()
    user1 = User(
        username="foodwise", hashed_password=pwd.hash("theclown")
    )
    user2 = User(
        username="roisin", hashed_password=pwd.hash("quinn")
    )
    user3 = User(
        username="cillian", hashed_password=pwd.hash("oriain")
    )
    user4 = User(
        username="darren", hashed_password=pwd.hash("counihan")
    )
    user5 = User(
        username="joana", hashed_password=pwd.hash("mafra")
    )
    req1 = UserRequest(
        field1="cillian", field2="darren", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req2 = UserRequest(
        field1="darren", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req3 = UserRequest(
        field1="cillian", field2="roisin", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req4 = UserRequest(
        field1="roisin", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req5 = UserRequest(
        field1="cillian", field2="joana", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req6 = UserRequest(
        field1="joana", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING
    )
    req7 = UserRequest(
        field1="cillian", field2="foodwise", type=RequestTypes.FOLLOW_REQUEST, status=Status.PENDING
    )
    req8 = UserRequest(
        field1="foodwise", field2="cillian", type=RequestTypes.FOLLOW_REQUEST, status=Status.ACCEPTED
    )
    req9 = UserRequest(
        field1="cillian", field2="darren", type=RequestTypes.CIRCLE_INVITE, status=Status.ACCEPTED
    )
    req10 = UserRequest(
        field1="darren", field2="cillian", type=RequestTypes.CIRCLE_INVITE, status=Status.PENDING
    )
    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.add(user4)
    db.add(user5)
    db.add(req1)
    db.add(req2)
    db.add(req3)
    db.add(req4)
    db.add(req5)
    db.add(req6)
    db.add(req7)
    db.add(req8)
    db.add(req9)
    db.add(req10)
    db.commit()