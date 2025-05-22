from typing import Optional
from pydantic import BaseModel, HttpUrl, field_serializer
from datetime import datetime

class SlackEventBase(BaseModel):
    url: str
    timestamp: datetime

class SlackEventCreate(SlackEventBase):
    user_id: int

from uuid import UUID

class SlackEventRead(SlackEventBase):
    id: UUID
    user_id: int

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info):
        return str(id)

    class Config:
        from_attributes = True

# --- 統計回傳 Schemas ---
class SlackCount(BaseModel):
    date: datetime
    count: int

class SlackUserStat(BaseModel):
    user_id: int
    count: int
    total_minutes: int

class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    is_authenticated: bool


class PolicyRequest(BaseModel):
    username: str
    url: str


class PolicyResponse(BaseModel):
    can_pass: bool
    token: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserUpdate(BaseModel):
    id: int
    username: Optional[str] = None
    password: Optional[str] = None
    mode: Optional[str] = None


class BlockedSiteCreate(BaseModel):
    host: str


class BlockedSiteUpdate(BaseModel):
    id: int
    host: str
