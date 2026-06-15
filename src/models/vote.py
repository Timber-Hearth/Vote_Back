from sqlalchemy import BigInteger, Column, ForeignKey, TIMESTAMP, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class Vote(Base):
    __tablename__ = "votes"

    __table_args__ = (
        UniqueConstraint("poll_group_qr", "anonymous_id", "option_id",name="uq_votes_poll_anon_option"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    poll_group_qr = Column(String(255), ForeignKey("poll_group.qr_token", ondelete="CASCADE"), nullable=False, index=True)
    option_id = Column(BigInteger, ForeignKey("poll_options.id", ondelete="CASCADE"), nullable=False, index=True)
    anonymous_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)
