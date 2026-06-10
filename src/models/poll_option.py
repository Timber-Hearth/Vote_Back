from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class PollOption(Base):
    __tablename__ = "poll_options"

    __table_args__ = (
        UniqueConstraint("poll_id", "display_order", name="uq_poll_options_poll_order"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    poll_id = Column(UUID(as_uuid=True), ForeignKey("polls.id", ondelete="CASCADE"), nullable=False, index=True)
    option_text = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=False)
