from sqlalchemy import Column, Boolean, Integer, TIMESTAMP
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from src.models.user import User

class Polls(Base):
    __tablename__ = "polls"
    id = Column(UUID, primary_key=True)
    owner_id = Column(BigInteger, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    
    is_public_result = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP)
    expire_at = Column(TIMESTAMP)
    
    allow_multiple_choice = Column(Boolean, default=False)
    delete_after_hours = Column(Integer, default=24)