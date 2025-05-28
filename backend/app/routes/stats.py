# app/api/slack_stats.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from database import get_db
import models, schemas
from models import User, SlackEvent
from urllib.parse import urlparse
from collections import defaultdict

TZ = timezone(timedelta(hours=8))

router = APIRouter(
    prefix="/api/stats/slack",
    tags=["Slack Stats"]
)

# ———— 你的原版 filter 函式 ————
def filter_distinct_visits(events, time_gap_seconds=30):
    """
    根據 (user_id, domain) 和 timestamp，濾除短時間內重複訪問
    """
    seen = {}  # key = (user_id, domain) -> last seen datetime
    result = []

    # 只用 timestamp 排序。假如有 None，就把它放到最前面
    def _ts(e):
        return e.timestamp or datetime.min

    for e in sorted(events, key=_ts):
        # optional: 跳過沒有 user_id 的事件
        if e.user_id is None:
            continue

        domain = urlparse(e.url).netloc
        key = (e.user_id, domain)
        last = seen.get(key)

        if not last or (e.timestamp - last) > timedelta(seconds=time_gap_seconds):
            result.append(e)
            seen[key] = e.timestamp

    return result

# ———— 幫你計算 cnt/minutes 的新函式 ————
def _user_stats_py(start: datetime, end: datetime, db: Session, user_id: int | None = None):
    # 1. 先抓原始事件
    q = db.query(SlackEvent).filter(
        SlackEvent.timestamp >= start,
        SlackEvent.timestamp <  end
    )
    if user_id:
        q = q.filter(SlackEvent.user_id == user_id)
    events = q.order_by(SlackEvent.timestamp).all()

    # 2. 用 filter_distinct_visits 去除同 domain 30 秒內重複
    events = filter_distinct_visits(events, time_gap_seconds=30)

    # 3. 依 user 分組，計算次數與總分鐘數
    by_user = defaultdict(list)
    for e in events:
        by_user[e.user_id].append(e)

    stats = []
    for uid, evs in by_user.items():
        evs.sort(key=lambda x: x.timestamp)
        cnt = len(evs)
        total_gap = 0.0
        prev_ts = None
        for e in evs:
            if prev_ts:
                gap = (e.timestamp - prev_ts).total_seconds()
                if gap <= 300:  # 5 分鐘內算同一 session
                    total_gap += gap
            prev_ts = e.timestamp
        minutes = int(total_gap / 60) + cnt
        stats.append(type("S", (), {"user_id": uid, "cnt": cnt, "minutes": minutes})())
    return stats

def _today_range():
    local = datetime.now(TZ).date()
    start = datetime.combine(local, datetime.min.time()).replace(tzinfo=TZ)
    end   = start + timedelta(days=1)
    return start, end

def _week_range():
    now = datetime.now(TZ)
    monday = (now - timedelta(days=now.weekday())).date()
    start = datetime.combine(monday, datetime.min.time()).replace(tzinfo=TZ)
    end   = start + timedelta(days=7)
    return start, end

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = db.query(User).get(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ———— 各路由改為呼叫 _user_stats_py ————
@router.get("/me/today", response_model=schemas.SlackUserStat)
def my_slack_today(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    start, end = _today_range()
    rows = _user_stats_py(start, end, db, user_id=current_user.id)
    row = rows[0] if rows else None
    return {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "count": row.cnt if row else 0,
        "total_minutes": row.minutes if row else 0
    }

@router.get("/users/today/top10", response_model=list[schemas.SlackUserStat])
def users_today_top10(db: Session = Depends(get_db)):
    start, end = _today_range()
    rows = _user_stats_py(start, end, db)
    # 按 cnt 排序取前 10
    top10 = sorted(rows, key=lambda r: r.cnt, reverse=True)[:10]
    out = []
    for r in top10:
        u = db.query(User).get(r.user_id)
        if r.user_id:
            out.append({
                "user_id": r.user_id,
                "user_name": u.name if u else f"#{r.user_id}",
                "count": r.cnt,
                "total_minutes": r.minutes
            })
    return out

@router.get("/users/today", response_model=list[schemas.SlackUserStat])
def users_today(db: Session = Depends(get_db)):
    start, end = _today_range()
    rows = _user_stats_py(start, end, db)
    return [
        {
            "user_id": r.user_id,
            "user_name": (db.query(User).get(r.user_id).name or f"#{r.user_id}"),
            "count": r.cnt,
            "total_minutes": r.minutes
        }
        for r in rows
    ]

@router.get("/users/week", response_model=list[schemas.SlackUserStat])
def users_week(db: Session = Depends(get_db)):
    start, end = _week_range()
    rows = _user_stats_py(start, end, db)
    return [
        {
            "user_id": r.user_id,
            "user_name": (db.query(User).get(r.user_id).name or f"#{r.user_id}"),
            "count": r.cnt,
            "total_minutes": r.minutes
        }
        for r in rows
    ]

@router.get("/online-friends", response_model=list[schemas.UserSummary])
def get_online_friends(db: Session = Depends(get_db)):
    cutoff = datetime.now(TZ) - timedelta(minutes=30)
    users = (
        db.query(User.id, User.name)
          .join(SlackEvent, User.id == SlackEvent.user_id)
          .filter(SlackEvent.timestamp >= cutoff)
          .distinct()
          .all()
    )
    return [{"user_id": u.id, "name": u.name} for u in users]

@router.get("/user/{user_id}/today", response_model=schemas.SlackUserStat)
def user_today(user_id: int, db: Session = Depends(get_db)):
    start, end = _today_range()
    rows = _user_stats_py(start, end, db, user_id=user_id)
    row = rows[0] if rows else None
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id":       u.id,
        "user_name":     u.name,
        "count":         row.cnt if row else 0,
        "total_minutes": row.minutes if row else 0
    }
