from sqlalchemy import Column, TIMESTAMP
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import DateTime

from src.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    password = Column(String(255))
    created_at = Column(TIMESTAMP)
    expire_at = Column(TIMESTAMP)