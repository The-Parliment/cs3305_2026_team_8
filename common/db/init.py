from common.db.engine import engine
from common.db.base import Base
from common.db.structures.structures import User
from passlib.context import CryptContext
from .db import get_db
import common.db.structures

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.create_all(bind=engine)
    temp_remove_in_production()


def temp_remove_in_production():
    db = get_db()
    user1 = User(
        "foodwise", pwd.hash("theclown")
    )
    user2 = User(
        "roisin", pwd.hash("quinn")
    )
    user3 = User(
        "cillian", pwd.hash("oriain")
    )
    db.add(user1)
    db.add(user2)
    db.add(user3)
    db.commit()