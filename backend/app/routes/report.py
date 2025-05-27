# app/routers/report.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from daily_report_sender import generate_and_send_report

router = APIRouter()

@router.post("/api/send_report")
async def send_daily_report(background_tasks: BackgroundTasks):
    """
    立刻觸發寄送今天的 Slack 划水報表，並在 background 執行。
    """
    try:
        background_tasks.add_task(generate_and_send_report)
        return {"detail": "Report sending triggered."}
    except Exception as e:
        # 若有任何錯誤，自動回 500
        raise HTTPException(status_code=500, detail=str(e))
