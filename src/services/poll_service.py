import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import UUID
from sqlalchemy.orm import Session

from src.models import PollOption, Polls, QrTokens
from src.schemas.poll import CreatePollRequest


def ServiceCreatePoll(db : Session, owner_id : int, request : CreatePollRequest):
    
    title = request.title
    description = request.description
    options = request.options
    allow_multiple_choice = request.allow_multiple_choice
    delete_after_hours = request.delete_after_hours
    is_public_result = request.is_public_result
    
    expire_at = datetime.now(UTC) + timedelta(hours=delete_after_hours)

    polls = Polls(
        owner_id = owner_id,
        title = title,
        description = description,
        is_closed = False,
        is_public_result = is_public_result,
        expire_at = expire_at,
        allow_multiple_choice = allow_multiple_choice,
        delete_after_hours = delete_after_hours,
    )
    db.add(polls)
    db.flush()

    for index, option_text in enumerate(options, start=1):
        option = PollOption(
            poll_id = polls.id,
            option_text = option_text,
            display_order = index,
        )
        db.add(option)

    qr_token_string = secrets.token_urlsafe(16)
    qr_token = QrTokens(
        poll_id = polls.id,
        tokens = qr_token_string
    )
    db.add(qr_token)
    db.commit()
    db.refresh(polls)
    
    return {
        "poll_id": str(polls.id),
        "token": qr_token_string
    }

def ServiceGetPoll(db : Session, token : str):
    qr_token = db.query(QrTokens).filter(QrTokens.tokens == token).first()
    if not qr_token:
        return None
    poll = db.query(Polls).filter(Polls.id == qr_token.poll_id).first()
    return poll

def ServiceGetOptionsFromPollID(db: Session, id : UUID):
    options = db.query(PollOption).filter(PollOption.poll_id == id).all()
    return options

