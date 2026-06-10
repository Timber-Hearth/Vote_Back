import os
import secrets
from datetime import UTC, datetime, timedelta
from sqlalchemy.orm import Session

from src.models import PollGroup
from src.repositories.poll_group_repository import Repo_GetPollGroupByToken
from src.models import Polls
from src.repositories.vote_repository import CalculateVoteCount
from src.schemas.requests.poll import CreatePollRequest
from src.repositories.poll_repository import (
    CreatePollOnDB,
)

def Service_CreatePoll(db: Session, request: CreatePollRequest, poll_group_id):
    title = request.title
    description = request.description
    options = request.options
    allow_multiple_choice = request.allow_multiple_choice
    poll_group_id = poll_group_id

    poll = CreatePollOnDB(
        db,
        title=title,
        description=description,
        poll_group_id=poll_group_id,
        options=options,
        allow_multiple_choice=allow_multiple_choice,
    )
    return {
        "poll_id": str(poll.id),
    }

# TODO : 이거 그룹으로 바꿔. 이거 호출할때 사용자 인증절차 넣어라
def Service_GetPollGroup(db: Session, token: str) -> PollGroup:
    return Repo_GetPollGroupByToken(db=db, token=token)

def PollPublicChecker(poll: Polls, current_user=None):
    if not poll.is_public_result:
        if not current_user:
            return False
        if poll.owner_id != current_user.id:
            return False
    return True


# TODO : 이걸 이용해서 응답 생성하자
def BuildFinalPollData(db: Session, poll_group: Polls, current_user = None) -> dict[str, object]:
    data = CalculateVoteCount(db, poll.id)
    options = ServiceGetOptionsFromPollID(db, poll.id)
    my_poll = False
    if current_user is not None:
        my_poll = True if poll.owner_id == current_user.id else False
    result = {
        "poll_data": {
            "id": str(poll.id),
            "owner_id": poll.owner_id,
            "my_poll" : my_poll,
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
