# app/services/daily_report_sender.py
from database import SessionLocal
from models import User, SlackEvent
from services.email_util import send_email

from datetime import datetime, timedelta, date
from urllib.parse import urlparse
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

def filter_distinct_visits(events, time_gap_seconds=30):
    """
    根據 (user_id, domain) 和 timestamp，濾除短時間內重複訪問
    """
    seen = {}  # key = (user_id, domain), value = last_seen_time
    result = []

    for event in sorted(events, key=lambda e: e.timestamp):  # 確保按時間排序
        domain = urlparse(event.url).netloc
        key = (event.user_id, domain)
        last_time = seen.get(key)

        if not last_time or (event.timestamp - last_time) > timedelta(seconds=time_gap_seconds):
            result.append(event)
            seen[key] = event.timestamp  # 更新時間

    return result

def generate_report_file(events: list[SlackEvent], filename: str) -> str:
    """
    將 SlackEvent 寫入報表檔案，回傳檔案路徑
    """
    path = Path("/tmp") / filename
    with path.open("w", encoding="utf-8") as f:
        f.write("timestamp,user_id,domain,url\n")
        for e in events:
            ts = e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            domain = urlparse(e.url).netloc
            f.write(f"{ts},{e.user_id},{domain},{e.url}\n")
    return str(path)

def get_recipient_emails(db) -> list[str]:
    """
    撈出所有有填 email 的使用者
    """
    return [u.email for u in db.query(User).filter(User.email != None).all() if u.email]

def get_all_events(db) -> list[SlackEvent]:
    """
    撈出所有 SlackEvent
    """
    return db.query(SlackEvent).order_by(SlackEvent.timestamp).all()

def generate_and_send_report():
    db = SessionLocal()
    try:
        # 1. 撈出所有使用者
        users = db.query(User).filter(User.email != None).all()
        if not users:
            print("❗ 沒有使用者，略過寄信")
            return

        # 2. 撈出今天的 SlackEvent（並排序）
        today = date.today()
        events = (
            db.query(SlackEvent)
            .filter(SlackEvent.timestamp >= today)
            .order_by(SlackEvent.timestamp)
            .all()
        )

        # 3. 過濾短時間內重複事件
        filtered_events = filter_distinct_visits(events)

        # 4. 依使用者 email 分組過濾後的事件

        user_events = defaultdict(list)
        
        for event in filtered_events:
            if event.user:
                domain = urlparse(event.url).netloc
                user_events[event.user.email].append(f"https://{domain}/")

        # 5. 逐人寄信
        for user in users:
            email = user.email
            urls = user_events.get(email, [])
            count = len(urls)
            if count <= 5:
                intro = "挺好的，請繼續內卷你的朋友😀\n"
            elif 6 <= count <= 25:
                intro = "你的 GPA 要被你划掉了😡\n"
            else:
                intro = "啊啊啊啊啊，別再混了！！！🤬"
            
            body = intro + f"你今天划水了 {count} 次。"
            if urls:
                body += "\n你划水了這些網站：\n" + "\n".join(urls)
            
            send_email(
                subject=f"[每日划水報告] {today}",
                body_text=body,
                to_emails=[email]
            )
            print(f"✅ 已寄信給 {email}（共 {count} 筆事件）")
    finally:
        db.close()

