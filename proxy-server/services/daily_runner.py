from apscheduler.schedulers.blocking import BlockingScheduler
from backend.app.daily_report_sender import generate_and_send_report

scheduler = BlockingScheduler(timezone="Asia/Taipei")

# 每天早上 09:00 觸發（你可以改 'cron' 參數）
scheduler.add_job(generate_and_send_report,
                  trigger="cron",
                  hour=9, minute=0)

print("[Runner] 排程器已啟動，等待執行任務…")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("\n[Runner] 排程器終止")
