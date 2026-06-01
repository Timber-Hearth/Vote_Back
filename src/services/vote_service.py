import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.orm import Session

from src.exceptions.vote import (
    VoteAlreadyCastError,
    VoteClosedError,
    VoteExpiredError,
    VoteMultipleChoiceNotAllowedError,
    VoteNoOptionError,
    VoteOptionNotFoundError,
    VotePollNotFoundError,
)
from src.models import Polls
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


def IsThatOptionReallyExist(user_select: Sequence[int], options: Sequence) -> bool:
    options_id = {x.id for x in options if x}
    return set(user_select).issubset(options_id)


def ServiceVoteProcess(
    db: Session,
    poll_data: Polls | None,
    selected_option_ids: Sequence[int],
    anonymous_id: uuid.UUID,
):
    if poll_data is None:
        raise VotePollNotFoundError()

    if poll_data.expire_at and poll_data.expire_at < datetime.now(UTC):
        raise VoteExpiredError()

    if poll_data.is_closed:
        raise VoteClosedError()

    if not selected_option_ids:
        raise VoteNoOptionError()

    if not poll_data.allow_multiple_choice and len(selected_option_ids) > 1:
        raise VoteMultipleChoiceNotAllowedError()

    options = GetOptionsByPollID(db, poll_data.id)
    if not options:
        raise VoteNoOptionError()

    if not IsThatOptionReallyExist(selected_option_ids, options):
        raise VoteOptionNotFoundError()

    if HasAnonymousVoteForOptionIDs(db, poll_data.id, anonymous_id, selected_option_ids):
        raise VoteAlreadyCastError()

    CreateVotes(db, poll_data.id, anonymous_id, selected_option_ids)

