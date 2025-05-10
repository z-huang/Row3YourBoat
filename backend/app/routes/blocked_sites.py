from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import *
from database import get_db
from schemas import *

router = APIRouter()


@router.post("/api/blocked_sites", response_model=dict)
def add_blocked_site(site: BlockedSiteCreate, db: Session = Depends(get_db)):
    exists = db.query(BlockedSites).filter_by(host=site.host).first()
    if exists:
        raise HTTPException(status_code=400, detail="Host already blocked.")
    new_site = BlockedSites(host=site.host)
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return {"id": new_site.id, "host": new_site.host}


@router.get("/api/blocked_sites", response_model=list[dict])
def get_blocked_sites(db: Session = Depends(get_db)):
    return [{"id": s.id, "host": s.host} for s in db.query(BlockedSites).all()]


@router.put("/api/blocked_sites", response_model=dict)
def update_blocked_site(site: BlockedSiteUpdate, db: Session = Depends(get_db)):
    target = db.query(BlockedSites).filter_by(id=site.id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Blocked site not found.")
    target.host = site.host
    db.commit()
    return {"id": target.id, "host": target.host}


@router.delete("/api/blocked_sites/{site_id}", response_model=dict)
def delete_blocked_site(site_id: int, db: Session = Depends(get_db)):
    target = db.query(BlockedSites).filter_by(id=site_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Blocked site not found.")
    db.delete(target)
    db.commit()
    return {"detail": "Deleted"}
