from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from urllib.parse import urlparse

from models import *
from database import get_db
from schemas import *
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer



router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/api/login", response_model=AuthResponse)
def login(auth_data: AuthRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == auth_data.username).first()
    if user and pwd_context.verify(auth_data.password, user.password):
        request.session["user_id"] = user.id
        return {"is_authenticated": True}
    return {"is_authenticated": False}


@router.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {"detail": "Logged out"}


@router.get("/api/users", response_model=list[dict])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.name, "mode": u.mode} for u in users]


@router.post("/api/users/create", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print(f"[CREATE] username={user.username} password={user.password}")
    existing = db.query(User).filter(User.name == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = pwd_context.hash(user.password)
    db_user = User(name=user.username, password=hashed, email=user.email, mode="normal")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.name, "mode": db_user.mode}

@router.put("/api/users", response_model=dict)
def update_user(update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=update.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update.username is not None:
        user.name = update.username
    if update.password is not None:
        user.password = pwd_context.hash(update.password)
    if update.mode is not None:
        user.mode = update.mode

    db.commit()
    return {"id": user.id, "username": user.name, "mode": user.mode}


@router.delete("/api/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "Deleted"}
