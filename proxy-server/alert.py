# alert.py
from services.email_util import send_email
from urllib.parse import urlparse
from datetime import datetime, timedelta
import sys
import os
import db


# key = user_id or username, value = last sent time
last_sent_time = {}

def notify_all_users_of_slack(username: str, url: str, db):
    now = datetime.now()

    # 冷卻機制
    if username in last_sent_time:
        if now - last_sent_time[username] < timedelta(seconds=30):
            print(f"⏳ 使用者 {username} 通知間隔未滿 30 秒，略過寄信")
            return

    last_sent_time[username] = now

    # 組內容
    domain = urlparse(url).netloc
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    recipients = db.get_all_user_emails()



    if not recipients:
        print("📭 無收件人，略過發信")
        return

    send_email(
        subject=f"[警告] {username} 剛剛打開了被封鎖網站！",
        body_text=(
            f"嗶嗶嗶 🚨\n\n"
            f"使用者 {username} 在 {time_str} 打開了被封鎖的網站：\n"
            f"👉 https://{domain}/\n\n"
            f"請大家互相監督（或私訊他 😏）\n\n"
            f"Row3YourBoat Bot 上線 🌊"
        ),
        to_emails=recipients
    )

    print(f"✅ 已寄信給所有人：{username}, 網站 {domain}")
