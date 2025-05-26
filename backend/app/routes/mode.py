from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, StringConstraints
from typing import Annotated

from models import *
from database import get_db
from schemas import *

router = APIRouter()


class ModeUpdate(BaseModel):
    access_mode: Annotated[
        str,
        StringConstraints(min_length=1, max_length=1, pattern="^[ABC]$")
    ]


class ModeResponse(BaseModel):
    access_mode: str


@router.get("/api/mode", response_model=ModeResponse)
def get_mode(db: Session = Depends(get_db)):
    mode = db.query(GlobalMode).filter_by(id=1).first()
    if not mode:
        raise HTTPException(status_code=404, detail="Global mode not set.")
    return {"access_mode": mode.access_mode}


@router.post("/api/mode", response_model=ModeResponse)
def set_mode(data: ModeUpdate, db: Session = Depends(get_db)):
    mode = db.query(GlobalMode).filter_by(id=1).first()
    if mode:
        mode.access_mode = data.access_mode
    else:
        mode = GlobalMode(id=1, access_mode=data.access_mode)
        db.add(mode)
    db.commit()
    return {"access_mode": mode.access_mode}
