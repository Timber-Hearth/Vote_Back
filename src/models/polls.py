import uuid

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class Polls(Base):
    __tablename__ = "polls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("poll_group.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    allow_multiple_choice = Column(Boolean, default=False)