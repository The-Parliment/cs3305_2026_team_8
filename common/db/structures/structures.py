from sqlalchemy import ForeignKey, Column, String, Integer, Float, Boolean, DateTime, Enum
from sqlalchemy import ForeignKey, Column, String, Integer, Float, Boolean, DateTime
from datetime import datetime, timezone
from ..base import Base
import enum

class RequestTypes(enum.Enum):
    FOLLOW_REQUEST = "follow_request" # Field1 requests to follow Field2
    CIRCLE_INVITE = "circle_invite" # Field1 invites Field2 into the Circle
    EVENT_INVITE = "event_invite" # Field1 invites Field2 to event Field3

class Status(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"


'''
    The Request table is incredibly varied and is designed so that data is derived from it.
    For instance, to find out if two users are friends, query if User A's follow request to User B
    has been accepted, and vice versa. 
'''
class UserRequest(Base):
    __tablename__ = "requests"

    field1 = Column("field1", String, primary_key=True) # Sender
    field2 = Column("field2", String, primary_key=True) # Receiver
    field3 = Column("field3", String, primary_key=True, default="") # Only used contextually
    type = Column("type", Enum(RequestTypes, create_constraint=True), primary_key=True)
    status = Column("status", Enum(Status, create_constraint=True), nullable=False, default=Status.PENDING)

class User(Base):
    __tablename__ = "users"

    username = Column("username", String, primary_key=True)
    hashed_password = Column("hashed_password", String)

class UserDetails(Base):
    __tablename__ = "user_details"

    username = Column("username", String, primary_key=True)
    first_name = Column("first_name", String, nullable=True)
    last_name = Column("last_name", String, nullable=True)
    email = Column("email", String, nullable=True)
    phone_number = Column("phone_number", String, nullable=True)
    
class Venue(Base):
    __tablename__ = "venues"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", String)
    latitude = Column("latitude", Float)
    longitude = Column("longitude", Float)

#Remove this, use UserRequest instead. This is just for testing purposes.
class Group(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column( String, nullable=False, index=True)
    group_desc = Column(String, index=True)
    is_private = Column(Boolean, index=True, default=False)   # True = Private, False = Public.
    owner = Column(String, ForeignKey("users.username"), index=True)  # Will change on cillians push
    dob = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(group_id={self.group_id}, group_name='{self.group_name}')>"

class GroupMembers(Base):
    __tablename__ = "groupjoins"
    join_id = Column(Integer, primary_key=True, autoincrement=True)  # need a real PK
    username = Column(String, ForeignKey("users.username"), index=True)
    group_id = Column(Integer, ForeignKey("groups.group_id"), index=True)
    date_joined = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"Joined group {group_id}!" 

class Events(Base):
    __tablename__ = "events"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    venue = Column("venue", String, default="") 
    latitude = Column("latitude", Float, nullable=True)
    longitude = Column("longitude", Float, nullable=True)
    datetime_start = Column("datetime_start", DateTime)
    datetime_end = Column("datetime_end", DateTime)
    title = Column("title", String)
    description = Column("description", String)
    host = Column("host", String, default="")
    
    host = Column("host", String, ForeignKey("users.username"), nullable=True)
