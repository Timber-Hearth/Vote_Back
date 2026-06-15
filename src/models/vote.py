from sqlalchemy import BigInteger, Column, ForeignKey, TIMESTAMP, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base

# TODO : 만약, 투표를 생성한다면 gcp pub/sub에 대기열을 추가해라. 클라우드 펑션으로 하나씩 꺼내서 qr 이미지를 만들고 서버에 저장한다

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
