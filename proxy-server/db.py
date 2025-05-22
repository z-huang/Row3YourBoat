from datetime import datetime
import os
import uuid
import asyncpg
from passlib.context import CryptContext


class Database:
    def __init__(self):
        self.pool = None
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host='db',
            port=5432,
            min_size=1,
            max_size=50
        )

    async def authenticate_user(self, username: str, password: str) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT password FROM users WHERE username = $1", username
            )
            if not row:
                return False
            return self.pwd_context.verify(row["password"], password)

    async def check_host(self, hostname: str) -> bool:
        query = "SELECT 1 FROM blocked_sites WHERE host = $1 LIMIT 1"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, hostname)
            return row is None

    async def record_slack(self, username: str, url: str) -> uuid.UUID:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT id FROM users WHERE username = $1", username
                )
                if not row:
                    raise ValueError(f"User '{username}' not found")
                user_id = row["id"]

                event_id = uuid.uuid4()
                timestamp = datetime.now()

                # Insert the slack event
                await conn.execute(
                    """
                    INSERT INTO slack_event (id, timestamp, user_id, url)
                    VALUES ($1, $2, $3, $4)
                    """,
                    event_id, timestamp, user_id, url
                )

                return event_id