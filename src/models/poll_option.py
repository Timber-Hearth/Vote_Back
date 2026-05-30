from psycopg.types import uuid
from sqlalchemy import Column, UUID, ForeignKey, Integer
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import DateTime

from models.polls import Polls
from src.core.database import Base

class PollOption(Base):
    __tablename__ = "poll_options"
    
    id = Column(BigInteger, primary_key=True)
    poll_id = Column(UUID, ForeignKey(Polls.id), nullable=False)
    option_text = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=False)