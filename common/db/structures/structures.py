from sqlalchemy import ForeignKey, Column, String, Integer, Float, Boolean, DateTime
from datetime import datetime, timezone
from ..base import Base

class User(Base):
    __tablename__ = "users"

    username = Column("username", String, primary_key=True)
    hashed_password = Column("hashed_password", String)

    def __init__(self, username, hashed_password):
        self.username = username
        self.hashed_password = hashed_password

    def __repr__(self):
        return f"{self.username}"

class UserDetails(Base):
    __tablename__ = "user_details"

    username = Column("username", String, ForeignKey("users.username"), primary_key=True)
    first_name = Column("first_name", String, nullable=True)
    last_name = Column("last_name", String, nullable=True)
    email = Column("email", String, nullable=True)
    phone_number = Column("phone_number", Integer, nullable=True)

    def __init__(self, username, first_name, last_name, email, phone_number):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number

    def __repr__(self):
        return f"{self.username}'s details"
    
class Venue(Base):
    __tablename__ = "venues"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", String)
    latitude = Column("latitude", Float)
    longitude = Column("longitude", Float)
    
    def __init__(self, name, latitude, longitude, id=None):
        if id is not None:
            self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"{self.name}"

class UserFollows(Base):
    __tablename__ = "user_follows"

    user1 = Column("user1", String, ForeignKey("users.username"), primary_key=True)
    user2 = Column("user2", String, ForeignKey("users.username"), primary_key=True)
    accepted = Column("accepted", Boolean, default=False)
    
    def __init__(self, user1, user2, accepted=False):
        self.user1 = user1
        self.user2 = user2
        self.accepted = accepted

    def __repr__(self):
        return f"{self.user1} requests to follow {self.user2}:" + "Approved" if self.accepted else "Pending"


class Friends(Base):
    __tablename__ = "friends"

    user1 = Column("user1", String, ForeignKey("users.username"), primary_key=True)
    user2 = Column("user2", String, ForeignKey("users.username"), primary_key=True)
    
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2

    def __repr__(self):
        return f"{self.user1} and {self.user2} are friends."

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


class InnerCircle(Base):
    __tablename__ = "inner_circle"

    user = Column("user", String, ForeignKey("users.username"), primary_key=True)
    user_in_circle = Column("user_in_circle", String, ForeignKey("users.username"), primary_key=True)
    
    def __init__(self, user, user_in_circle):
        self.user = user
        self.user_in_circle = user_in_circle

    def __repr__(self):
        return f"{self.user_in_circle} is in {self.user}'s inner circle."

class Events(Base):
    __tablename__ = "events"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    venue = Column("venue", String, ForeignKey("venues.id"))
    datetime = Column("datetime", DateTime)
    title = Column("title", String)
    description = Column("description", String)
    host = Column("host", String, ForeignKey("users.username"), nullable=True)
    
    def __init__(self, venue, datetime, title, description, host=None, id=None):
        if id is not None:
            self.id = id
        if host is not None:
            self.host = host
        self.venue = venue
        self.datetime = datetime
        self.title = title
        self.description = description

    def __repr__(self):
        return f"{self.title}"

class AttendingEvent(Base):
    __tablename__ = "attending_event"

    user = Column("user", String, ForeignKey("users.username"), primary_key=True)
    event = Column("event", String, ForeignKey("events.id"), primary_key=True)
    
    def __init__(self, user, event):
        self.user = user
        self.event = event

    def __repr__(self):
        return f"{self.user} is attending {self.event}"
