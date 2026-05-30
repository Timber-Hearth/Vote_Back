from sqlalchemy import BigInteger, Column, UUID, ForeignKey, String, TIMESTAMP

from core.database import Base
from models.polls import Polls


class QrTokens(Base):
    __tablename__ = "qr_tokens"
    
    id = Column(UUID, primary_key=True)
    poll_id = Column(UUID, ForeignKey(Polls.id))
    tokens = Column(String)
    created_at = Column(TIMESTAMP)