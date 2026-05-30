import os

from sqlalchemy import create_engine
from sqlalchemy.ext import declarative
from sqlalchemy.future import engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def GetDB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()