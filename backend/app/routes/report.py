# app/routers/report.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from daily_report_sender import generate_and_send_report
from database import SessionLocal
from models import User

router = APIRouter()

@router.post("/api/send_report")
async def send_daily_report(background_tasks: BackgroundTasks):
    """
    立刻觸發寄送今天的 Slack 划水報表，並在 background 執行。
    """
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.email != None).all()
    finally:
        db.close()

    if not users:
        # 找不到就回 400，前端 fetch 不會進到成功分支
        raise HTTPException(status_code=400, detail="沒有使用者信箱")
    try:
        background_tasks.add_task(generate_and_send_report)
        return {"detail": "寄出去了"}
    except Exception as e:
        # 若有任何錯誤，自動回 500
        raise HTTPException(status_code=500, detail=str(e))

