from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from models import PollOption, Polls
from schemas.poll import CreatePollRequest


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

    db.commit()
    db.refresh(polls)
    return polls
