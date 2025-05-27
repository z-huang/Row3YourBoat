# ----- ③ SlackEvent Router -----
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

import models, schemas
from database import get_db

router = APIRouter(
    prefix="/api/slack-events",
    tags=["Slack Events"]
)

# -------- Create --------
@router.post("/", response_model=schemas.SlackEventRead, status_code=status.HTTP_201_CREATED)
def create_slack_event(event_in: schemas.SlackEventCreate, db: Session = Depends(get_db)):
    db_event = models.SlackEvent(**event_in.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# -------- List --------
@router.get("/", response_model=list[schemas.SlackEventRead])
def list_slack_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(models.SlackEvent).offset(skip).limit(limit).all()
    return events


# -------- Retrieve (by UUID) --------
@router.get("/{event_id}", response_model=schemas.SlackEventRead)
def get_slack_event(event_id: UUID, db: Session = Depends(get_db)):
    event = db.query(models.SlackEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# -------- Delete --------
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slack_event(event_id: UUID, db: Session = Depends(get_db)):
    event = db.query(models.SlackEvent).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()


@router.get("/token/{token}", response_model=schemas.TokenUserInfo)
def get_user_info_by_token(token: str, db: Session = Depends(get_db)):
    try:
        # Convert token string to UUID
        token_uuid = UUID(token)
        # Query the event using the UUID and join with User table
        event = db.query(models.SlackEvent).join(models.User).filter(models.SlackEvent.id == token_uuid).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {
            "id": event.id,
            "user_id": event.user_id,
            "name": event.user.name,
            "url": event.url
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token format")