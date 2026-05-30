import uuid

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class Polls(Base):
    __tablename__ = "polls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    is_public_result = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    expire_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)

    allow_multiple_choice = Column(Boolean, default=False)
    delete_after_hours = Column(Integer, default=24)