from uuid import UUID

from sqlalchemy import Column, UUID, ForeignKey, Integer, TIMESTAMP
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import DateTime

from api.v1 import polls
from core.database import Base
from models.polls import Polls


class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(BigInteger, primary_key=True)
    poll_id = Column(UUID, ForeignKey(Polls.id), primary_key=True)
    anonymous_id = Column(UUID, nullable=True)
    created_at = Column(TIMESTAMP)