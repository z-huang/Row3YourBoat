from typing import Optional
from pydantic import BaseModel


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
