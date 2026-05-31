import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from backend/.env regardless of launch directory.
_BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(_BASE_DIR / ".env", encoding="utf-8-sig")

DATABASE_URL = "sqlite+pysqlite:///./secretvote.db"
env_database_url = os.environ.get("DATABASE_URL")
if env_database_url:
    DATABASE_URL = env_database_url

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

db_engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=db_engine,
)

# Backward compatibility for existing imports.
engine = db_engine

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


GetDB = get_db


