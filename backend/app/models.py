import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)  # hashed
    email = Column(String, unique=True) 

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


class GlobalMode(Base):
    """
    只有一列 (id = 1)。access_mode: 'A' | 'B' | 'C'
    """
    __tablename__ = "global_mode"

    id = Column(Integer, primary_key=True, default=1)
    access_mode = Column(String(1), nullable=False)

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_global_mode_single_row"),
        CheckConstraint("access_mode IN ('A','B','C')",
                        name="ck_global_mode_valid_values"),
    )
