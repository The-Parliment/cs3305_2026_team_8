# Schema file to create table.

from sqlalchemy import ForeignKey, Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class DBGroup(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column( String, nullable=False, index=True)
    group_desc = Column(String, index=True)
    is_private = Column(Boolean, index=True, default=False)   # True = Private, False = Public.
    owner = Column(String, index=True)  # Will change on cillians push
    dob = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(group_id={self.group_id}, group_name='{self.group_name}')>"

