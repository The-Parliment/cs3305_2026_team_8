from sqlalchemy import ForeignKey, Column, String, Integer, Float, Boolean, DateTime, Enum
from ..base import Base
import enum

class RequestTypes(enum.Enum):
    FRIEND_REQUEST = "friend_request"
    FOLLOW_REQUEST = "follow_request"
    CIRCLE_INVITE = "circle_invite"
    EVENT_INVITE = "event_invite"

class Status(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"

class Request(Base):
    __tablename__ = "requests"

    field1 = Column("field1", String, primary_key=True)
    field2 = Column("field2", String, primary_key=True)
    type = Column("type", Enum(RequestTypes, create_constraint=True), primary_key=True)
    status = Column("status", Enum(Status, create_constraint=True))

class User(Base):
    __tablename__ = "users"

    username = Column("username", String, primary_key=True)
    hashed_password = Column("hashed_password", String)

class UserDetails(Base):
    __tablename__ = "user_details"

    username = Column("username", String, ForeignKey("users.username"), primary_key=True)
    first_name = Column("first_name", String, nullable=True)
    last_name = Column("last_name", String, nullable=True)
    email = Column("email", String, nullable=True)
    phone_number = Column("phone_number", Integer, nullable=True)
    
class Venue(Base):
    __tablename__ = "venues"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", String)
    latitude = Column("latitude", Float)
    longitude = Column("longitude", Float)
    
class Events(Base):
    __tablename__ = "events"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    venue = Column("venue", String, ForeignKey("venues.id"))
    latitude = Column("latitude", Float, nullable=True)
    longitude = Column("longitude", Float, nullable=True)
    datetime = Column("datetime", DateTime)
    title = Column("title", String)
    description = Column("description", String)
    host = Column("host", String, ForeignKey("users.username"), nullable=True)

class UserFollows(Base):
    __tablename__ = "user_follows"

    user1 = Column("user1", String, ForeignKey("users.username"), primary_key=True)
    user2 = Column("user2", String, ForeignKey("users.username"), primary_key=True)
    accepted = Column("accepted", Boolean, default=False)


class Friends(Base):
    __tablename__ = "friends"

    user1 = Column("user1", String, ForeignKey("users.username"), primary_key=True)
    user2 = Column("user2", String, ForeignKey("users.username"), primary_key=True)

class InnerCircle(Base):
    __tablename__ = "inner_circle"

    user = Column("user", String, ForeignKey("users.username"), primary_key=True)
    user_in_circle = Column("user_in_circle", String, ForeignKey("users.username"), primary_key=True)


class AttendingEvent(Base):
    __tablename__ = "attending_event"

    user = Column("user", String, ForeignKey("users.username"), primary_key=True)
    event = Column("event", String, ForeignKey("events.id"), primary_key=True)
    