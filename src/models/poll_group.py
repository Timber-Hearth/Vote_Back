import uuid

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Text, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class PollGroup(Base):
    __tablename__ = "poll_group"
    
    __table_args__ = (
        UniqueConstraint("qr_token"),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=True)

    qr_token = Column(String(255), nullable=False)

    is_public_result = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    expire_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)

    delete_after_hours = Column(Integer, default=24)