from sqlalchemy import BigInteger, Column, String, TIMESTAMP, text

from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    login_id = Column(String(64), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    expire_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
