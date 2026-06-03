import os
import secrets
from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session

from core.redis_client import get_redis
from src.models import Polls
from src.repositories.vote_repository import CalculateVoteCount
from src.schemas.poll import CreatePollRequest
from src.repositories.poll_repository import (
    CreatePollWithOptionsAndToken,
    GetOptionsByPollID,
    GetPollByToken,
    GetPollByID,
)


def ServiceCreatePoll(db: Session, owner_id: int, request: CreatePollRequest):
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

def ServiceGetPoll(db: Session, token: str):
    return GetPollByToken(db, token)

def ServiceGetOptionsFromPollID(db: Session, poll_id):
    return GetOptionsByPollID(db, poll_id)

def IsThisPollCanSeeAnyone(db: Session, poll_id):
    poll_data = GetPollByID(db, poll_id)
    if poll_data is None:
        return False
    if poll_data.is_public_result:
        return True
    return False

def PollPublicChecker(poll: Polls, current_user=None):
    if not poll.is_public_result:
        if not current_user:
            return False
        if poll.owner_id != current_user.id:
            return False
    return True

def BuildFinalPollData(db: Session, poll: Polls) -> dict[str, object]:
    data = CalculateVoteCount(db, poll.id)
    options = ServiceGetOptionsFromPollID(db, poll.id)
    result = {
        "poll_data": {
            "id": str(poll.id),
            "owner_id": poll.owner_id,
            "title": poll.title,
            "description": poll.description,
            "is_public_result": poll.is_public_result,
            "is_closed": poll.is_closed,
            "allow_multiple_choice": poll.allow_multiple_choice,
            "expire_at": poll.expire_at,
            "created_at": poll.created_at,
        },
        "options": [{
            "option_id": opt.id,
            "option_text": opt.option_text,
            "count": data.get(opt.id, 0),
        }
            for opt in options
        ]}
    return result


def SetPollClose(db: Session, poll: Polls):
    try:
        poll.is_closed = True
        db.commit()
        db.refresh(poll)
        return True
    except Exception as e:
        db.rollback()
        print(e)
        return False

def RemoveSinglePoll(db: Session, poll: Polls):
    try:
        db.delete(poll)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(e)
        return False

def DeletePollResultFromRedis(poll_data: type[Polls]):
    try:
        redis = get_redis()
        key = f"{os.environ.get('REDIS_KEY_POLL_RESULT')}{poll_data.id}"
        redis.delete(key)
    except Exception as exc:
        print(exc)