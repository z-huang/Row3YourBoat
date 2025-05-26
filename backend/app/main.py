import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext

from models import *
from database import engine, SessionLocal
from schemas import *
from routes import users, blocked_sites, slack_events, stats, mode


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from models import GlobalMode
    if not db.query(GlobalMode).filter_by(id=1).first():
        db.add(GlobalMode(id=1, access_mode='A'))
        db.commit()
    db.close()


init_db()

app = FastAPI()
app.add_middleware(SessionMiddleware,
                   secret_key=os.getenv('BACKEND_SECRET_KEY'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(blocked_sites.router)
app.include_router(slack_events.router)
app.include_router(stats.router)
app.include_router(mode.router)
