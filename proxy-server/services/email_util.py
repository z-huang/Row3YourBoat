import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

SMTP_SERVER   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(subject: str,
               body_text: str,
               to_emails: list[str],
               attachment_path: str | None = None) -> None:
    """
    寄送 Email，支援純文字 body + 可選附件
    """

    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("請先設定 SMTP_USER / SMTP_PASSWORD 環境變數")

    msg             = MIMEMultipart()
    msg["From"] = f"🏖 Row Row Row Your Boat Server <{SMTP_USER}>"
    msg["To"]       = ", ".join(to_emails)
    msg["Subject"]  = subject
    msg.attach(MIMEText(body_text, "plain"))

    # 如有附件
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    print("[EmailUtil] 信件已送出 ➜", to_emails)
