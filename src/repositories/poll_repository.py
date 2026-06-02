import dbm
from collections.abc import Sequence

from certifi import where
from select import select
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import PollOption, Polls, QrTokens


def CreatePollWithOptionsAndToken(
    db: Session,
    *,
    owner_id: int,
    title: str,
    description: str | None,
    options: Sequence[str],
    allow_multiple_choice: bool,
    is_public_result: bool,
    expire_at,
    delete_after_hours: int,
    token: str,
):
    poll = Polls(
        owner_id=owner_id,
        title=title,
        description=description,  # type: ignore[arg-type]
        is_closed=False,
        is_public_result=is_public_result,
        expire_at=expire_at,
        allow_multiple_choice=allow_multiple_choice,
        delete_after_hours=delete_after_hours,
    )
    db.add(poll)
    db.flush()

    option_instances = [
        PollOption(
            poll_id=poll.id,
            option_text=option_text,
            display_order=index,
        )
        for index, option_text in enumerate(options, start=1)
    ]
    db.add_all(option_instances)

    qr_token = QrTokens(
        poll_id=poll.id,
        tokens=token,
    )
    db.add(qr_token)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(poll)
    return poll, token

def GetPollListByUserId(db: Session, user_id):
    return db.query(Polls).filter(Polls.owner_id == user_id).all()

def GetPollByID(db: Session, poll_id):
    return db.query(Polls).filter(Polls.id == poll_id).first()

def GetPollByToken(db: Session, token: str):
    qr_token = db.query(QrTokens).filter(QrTokens.tokens == token).first()
    if not qr_token:
        return None

    return db.query(Polls).filter(Polls.id == qr_token.poll_id).first()


def GetOptionsByPollID(db: Session, poll_id):
    return db.query(PollOption).filter(PollOption.poll_id == poll_id).all()

def GetQRTokenByOwnerAndPoll(db: Session, owner_id, poll_id): # TODO : 언젠간 쓰겠지
    poll_exists = db.query(Polls).filter(
        Polls.id == poll_id,
        Polls.owner_id == owner_id
    ).first()

    if not poll_exists:
        return None
    
    token = db.query(QrTokens).filter(
        QrTokens.poll_id == poll_id
    ).first()

    return token.tokens

