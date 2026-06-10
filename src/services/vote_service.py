import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from models import PollGroup
from repositories.poll_group_repository import Repo_GetPollListByToken
from src.schemas.requests import VoteRequest
from src.exceptions.vote import (
    VoteAlreadyCastError,
    VoteClosedError,
    VoteExpiredError,
    VoteMultipleChoiceNotAllowedError,
    VoteNoOptionError,
    VoteOptionNotFoundError,
    VotePollNotFoundError,
)
from src.repositories.vote_repository import (
    CreateVotes,
    GetOptionsByPollID,
    HasAnonymousVoteForOptionIDs,
)


def GetAnonymousId(request: Request) -> str | None:
    return request.cookies.get("anonymous_id")


def NormalizeAnonymousId(anonymous_id: str | None) -> tuple[uuid.UUID, bool]:
    if anonymous_id is None:
        return uuid.uuid4(), True

    try:
        return uuid.UUID(str(anonymous_id)), False
    except (TypeError, ValueError, AttributeError):
        return uuid.uuid4(), True

def ServiceVoteProcess(
    db: Session,
    poll_group_data: PollGroup | None,
    request: VoteRequest,
    anonymous_id: uuid.UUID,
):
    if poll_group_data is None:
        raise VotePollNotFoundError()

    if poll_group_data.expire_at and poll_group_data.expire_at < datetime.now(UTC):
        raise VoteExpiredError()

    if poll_group_data.is_closed:
        raise VoteClosedError()

    if not request.vote_data:
        raise VoteNoOptionError()

    polls = Repo_GetPollListByToken(db=db, token=poll_group_data.qr_token)
    for item in polls:
        if not item.allow_multiple_choice and len(request.vote_data.get(item.id)) > 1:
            raise VoteMultipleChoiceNotAllowedError()

        options = GetOptionsByPollID(db, item.id)
        if not options:
            raise VoteNoOptionError()

        if HasAnonymousVoteForOptionIDs(db, item.id, anonymous_id, request.vote_data.get(item.id)):
            raise VoteAlreadyCastError()

    CreateVotes(db, poll_group_data, anonymous_id, request)

