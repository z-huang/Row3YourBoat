import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)  # hashed
    email = Column(String, unique=True) 
    mode = Column(String)

    events = relationship("SlackEvent", back_populates="user")


class BlockedSites(Base):
    __tablename__ = "blocked_sites"
    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, index=True)


class SlackEvent(Base):
    __tablename__ = "slack_event"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(Text)

    user = relationship("User", back_populates="events")
