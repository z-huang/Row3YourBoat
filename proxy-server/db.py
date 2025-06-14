from datetime import datetime
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

from enum import Enum


class AccessMode(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class Database:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.conn = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
            host="db",
            port=5432
        )
        self.conn.autocommit = True

    def authenticate_user(self, username: str, password: str) -> bool:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT password FROM users WHERE name = %s", (username,))
            row = cur.fetchone()
            if not row:
                return False
            return self.pwd_context.verify(password, row["password"])

    def check_host(self, hostname: str) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM blocked_sites WHERE host = %s LIMIT 1", (hostname,))
            row = cur.fetchone()
            return row is None

    def record_slack(self, username: str, url: str) -> uuid.UUID:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE name = %s", (username,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"User '{username}' not found")
            user_id = row["id"]

            event_id = uuid.uuid4()
            timestamp = datetime.now()

            cur.execute("""
                INSERT INTO slack_event (id, timestamp, user_id, url)
                VALUES (%s, %s, %s, %s)
            """, (str(event_id), timestamp, user_id, url))

            return event_id

    def get_global_mode(self) -> AccessMode:
        with self.conn.cursor() as cur:
            cur.execute("SELECT access_mode FROM global_mode WHERE id = 1")
            row = cur.fetchone()             # row 如 ('B',) 或 None
            return AccessMode(row[0]) if row else AccessMode.A

    def set_global_mode(self, mode: AccessMode):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO global_mode (id, access_mode)
                VALUES (1, %s)
                ON CONFLICT (id) DO UPDATE SET access_mode = EXCLUDED.access_mode
            """, (mode.value,))

    def get_user_email(self, username: str) -> str:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT email FROM users WHERE name = %s", (username,))
            row = cur.fetchone()
            if not row or not row["email"]:
                raise ValueError(f"找不到 {username} 的 email")
            return row["email"]

    def get_all_user_emails(self) -> list[str]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT email FROM users WHERE email IS NOT NULL")
            rows = cur.fetchall()
            return [row["email"] for row in rows]
