import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from models import Polls
from src.schemas.poll import CreatePollRequest
from src.repositories.poll_repository import (
    CreatePollWithOptionsAndToken,
    GetOptionsByPollID,
    GetPollByToken, GetPollByID,
)


def ServiceCreatePoll(db : Session, owner_id : int, request : CreatePollRequest):
    title = request.title
    description = request.description
    options = request.options
    allow_multiple_choice = request.allow_multiple_choice
    delete_after_hours = request.delete_after_hours
    is_public_result = request.is_public_result
    
    expire_at = datetime.now(UTC) + timedelta(hours=delete_after_hours)

    qr_token_string = secrets.token_urlsafe(16)
    poll, token = CreatePollWithOptionsAndToken(
        db,
        owner_id=owner_id,
        title=title,
        description=description,
        options=options,
        allow_multiple_choice=allow_multiple_choice,
        is_public_result=is_public_result,
        expire_at=expire_at,
        delete_after_hours=delete_after_hours,
        token=qr_token_string,
    )
    return {
        "poll_id": str(poll.id),
        "token": token,
    }

def ServiceGetPoll(db : Session, token : str):
    return GetPollByToken(db, token)

def ServiceGetOptionsFromPollID(db: Session, id):
    return GetOptionsByPollID(db, id)

def IsThisPollCanSeeAnyone(db: Session, poll_id):
    poll_data = GetPollByID(db, poll_id)
    if poll_data.is_public_result:
        return True
    return False

