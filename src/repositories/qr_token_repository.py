import secrets

from sqlalchemy.orm import Session

from models import PollGroup
from src.models import QrTokens


def Repo_CreateQrToken(db: Session, poll_group: PollGroup) -> QrTokens:
    try:
        token = secrets.token_urlsafe(16)
        qr_token = QrTokens(
            poll_group_id=poll_group.id,
            tokens=token,
        )
        db.add(qr_token)
        db.commit()
        return qr_token

    except Exception as e:
        db.rollback()
        print(e)
        return None