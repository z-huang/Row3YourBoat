from app.services.email_util import send_email

# 測試內容
send_email(
    subject="測試信件 - 測試中",
    body_text="這是來自你的測試信件，恭喜你測試成功！",
    to_emails=["b11902143@csie.ntu.edu.tw"],  # 改成你的真實 email
    attachment_path=None  # 也可以放測試檔案路徑
)
