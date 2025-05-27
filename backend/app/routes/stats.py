from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta, timezone
from database import get_db
import models, schemas
from fastapi import Request
from models import User
from sqlalchemy import case, Integer
from sqlalchemy.sql import extract
from sqlalchemy.sql.expression import over
import jwt

TZ = timezone(timedelta(hours=8))

router = APIRouter(
    prefix="/api/stats/slack",
    tags=["Slack Stats"]
)

def _today_range():
    today = datetime.now(TZ).date() 
    start = datetime.combine(today, datetime.min.time()).astimezone(TZ)
    end   = start + timedelta(days=1)
    return start, end, today


def _week_range():
    now = datetime.now(TZ)
    monday = (now - timedelta(days=now.weekday())).date()          # 本週一
    start = datetime.combine(monday, datetime.min.time()).astimezone(TZ)
    end   = start + timedelta(days=7)
    return start, end

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    從 session 取得目前登入的 User，給其他路由當依賴使用。
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def _user_stats(start, end, db, user_id: int | None = None):
    base = (
        db.query(
            models.SlackEvent.user_id.label("user_id"),
            models.SlackEvent.timestamp.label("timestamp"),
            func.extract(
                "epoch",
                models.SlackEvent.timestamp
                - func.lag(models.SlackEvent.timestamp).over(
                    partition_by=models.SlackEvent.user_id,
                    order_by=models.SlackEvent.timestamp
                )
            ).label("gap")
        )
        .filter(models.SlackEvent.timestamp >= start,
                models.SlackEvent.timestamp <  end)
    )
    if user_id:
        base = base.filter(models.SlackEvent.user_id == user_id)

    subquery = base.subquery()

    result = (
        db.query(
            subquery.c.user_id,
            func.count(subquery.c.timestamp).label("cnt"),
            func.cast(
                (
                    func.coalesce(func.sum(
                        case((subquery.c.gap <= 300, subquery.c.gap), else_=0)
                    ), 0) / 60
                ) + func.count(subquery.c.timestamp),
                Integer
            ).label("minutes")
        )
        .group_by(subquery.c.user_id)
        .all()
    )
    return result

# ---------- 個人今日 ----------
@router.get("/me/today", response_model=schemas.SlackUserStat)
def my_slack_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start, end, _ = _today_range()
    rows = _user_stats(start, end, db, user_id=current_user.id)
    row = rows[0] if rows else None
    return {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "count": row.cnt if row else 0,
        "total_minutes": row.minutes if row else 0
    }

@router.get("/users/today/top10", response_model=list[schemas.SlackUserStat])
def users_today_top10(db: Session = Depends(get_db)):
    # 取得今日範圍
    start, end, _ = _today_range()
    # 拿到所有使用者今天的統計
    rows = _user_stats(start, end, db)
    # 依 total_minutes 排序，取前 10
    top10 = sorted(rows, key=lambda r: r.cnt, reverse=True)[:10]
    # 回傳格式化好的 list
    result = []
    for r in top10:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "user_id": r.user_id,
            "user_name": user.name if user else f"#{r.user_id}",
            "count": r.cnt,
            "total_minutes": r.minutes
        })
    return result

@router.get("/users/today", response_model=list[schemas.SlackUserStat])
def users_today(db: Session = Depends(get_db)):
    start, end, _ = _today_range()
    rows = _user_stats(start, end, db)

    result: list[dict] = []
    for r in rows:
        # 去 User table 找到對應的使用者
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "user_id":       r.user_id,
            "user_name":     user.name if user else f"#{r.user_id}",
            "count":         r.cnt,
            "total_minutes": r.minutes
        })
    return result

@router.get("/users/week", response_model=list[schemas.SlackUserStat])
def users_week(db: Session = Depends(get_db)):
    start, end = _week_range()
    rows = _user_stats(start, end, db)

    result: list[dict] = []
    for r in rows:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append({
            "user_id":       r.user_id,
            "user_name":     user.name if user else f"#{r.user_id}",
            "count":         r.cnt,
            "total_minutes": r.minutes
        })
    return result

@router.get("/online-friends", response_model=list[schemas.UserSummary])
def get_online_friends(db: Session = Depends(get_db)):
    now = datetime.now(TZ)
    one_min_ago = now - timedelta(minutes=30)

    users = (
        db.query(models.User.id, models.User.name)
        .join(models.SlackEvent, models.User.id == models.SlackEvent.user_id)
        .filter(models.SlackEvent.timestamp >= one_min_ago)
        .distinct()
        .all()
    )

    return [{"user_id": u.id, "name": u.name} for u in users]