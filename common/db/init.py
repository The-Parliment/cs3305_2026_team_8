from common.db.engine import engine
from common.db.base import Base
from common.db.structures.structures import User, UserDetails, UserRequest, RequestTypes, Status
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
    user1_details = UserDetails(
        username="foodwise", first_name="Food", last_name="Wise", email="foodwise@example.com", phone_number="01234567890"
    )
    user2 = User(
        username="roisin", hashed_password=pwd.hash("quinn")
    )
    user2_details = UserDetails(
        username="roisin", first_name="Roisin", last_name="Quinn", email="roisin@example.com", phone_number="01234567891"
    )
    user3 = User(
        username="cillian", hashed_password=pwd.hash("oriain")
    )
    user3_details = UserDetails(
        username="cillian", first_name="Cillian", last_name="Oriain", email="cillian@example.com", phone_number="01234567892"
    )
    user4 = User(
        username="darren", hashed_password=pwd.hash("counihan")
    )
    user4_details = UserDetails(
        username="darren", first_name="Darren", last_name="Counihan", email="darren@example.com", phone_number="01234567893"
    )
    user5 = User(
        username="joana", hashed_password=pwd.hash("mafra")
    )
    user5_details = UserDetails(
        username="joana", first_name="Joana", last_name="Mafra", email="joana@example.com", phone_number="01234567894"
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
    db.add(user1_details)
    db.add(user2_details)
    db.add(user3_details)
    db.add(user4_details)
    db.add(user5_details)
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