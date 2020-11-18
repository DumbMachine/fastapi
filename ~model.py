from sqlalchemy import Column, Integer, String, ForeignKey
from fastapi_sqlalchemy import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = "event"
    id = Column("id", Integer, primary_key=True)
    title = Column("title", String)
    image = Column("image", String)
    endTime = Column("endTime", String)
    waitlist = Column("waitlist", String)
    location = Column("location", String)
    startTime = Column("startTime", String)
    eventDate = Column("eventDate", String)
    description = Column("description", String)
    allowedAttendees = Column("allowedAttendees", String)


class User(Base):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    email = Column("email", String)
    eid = Column("eid", String, ForeignKey("event.id"), nullable=False)
