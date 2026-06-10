from collections.abc import Sequence

from sqlalchemy.orm import Session

from src.models import PollOption, Polls, QrTokens
from src.repositories.id_allocator import AllocateNextBigIntIds


def CreatePollOnDB(
    db: Session,
    title: str,
    description: str,
    poll_group_id: int,
    options: Sequence[str],
    allow_multiple_choice: bool,
):
    poll = Polls(
        title=title,
        description=description,
        group_id=poll_group_id,
        allow_multiple_choice=allow_multiple_choice,
    )
    db.add(poll)
    db.flush()

    option_ids = AllocateNextBigIntIds(db, PollOption, count=len(options))
    option_instances = [
        PollOption(
            id=option_id,
            poll_id=poll.id,
            option_text=option_text,
            display_order=index,
        )
        for option_id, (index, option_text) in zip(option_ids, enumerate(options, start=1))
    ]
    if hasattr(db, "add_all"):
        db.add_all(option_instances)
    else:
        for option in option_instances:
            db.add(option)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(poll)
    return poll

def GetPollListByUserId(db: Session, user_id):
    polls = db.query(Polls).filter(Polls.owner_id == user_id).all()
    if len(polls) < 1:
        return []
    poll_ids = [p.id for p in polls]
    tokens = db.query(QrTokens).filter(QrTokens.poll_id.in_(poll_ids)).all()
    token_map = {t.poll_id: t.tokens for t in tokens}
    
    return [
        {
            "title": p.title,
            "description": p.description,
            "is_closed": p.is_closed,
            "allow_multiple_choice": p.allow_multiple_choice,
            "delete_after_hours": p.delete_after_hours,
            "is_public_result": p.is_public_result,
            "created_at": p.created_at,
            "expire_at": p.expire_at,
            "qr_token": token_map.get(p.id, "")
        }
        for p in polls
    ]
    

def GetPollByID(db: Session, poll_id):
    return db.query(Polls).filter(Polls.id == poll_id).first()

def GetPollByToken(db: Session, token: str):
    qr_token = db.query(QrTokens).filter(QrTokens.tokens == token).first()
    if not qr_token:
        return None

    return db.query(Polls).filter(Polls.id == qr_token.poll_id).first()


def GetOptionsByPollID(db: Session, poll_id):
    return db.query(PollOption).filter(PollOption.poll_id == poll_id).all()

def GetQRTokenByOwnerAndPoll(db: Session, owner_id, poll_id):
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