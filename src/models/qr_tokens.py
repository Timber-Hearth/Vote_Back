from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
import uuid

class QrTokens(Base):
    __tablename__ = "qr_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, autoincrement=True)
    poll_group_id = Column(UUID(as_uuid=True), ForeignKey("poll_group.id", ondelete="CASCADE"), nullable=False, index=True)
    tokens = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
