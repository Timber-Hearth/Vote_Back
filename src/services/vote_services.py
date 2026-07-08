import uuid

from src.exceptions.vote import (
    VoteAlreadyCastError,
    VoteInvalidPollIdError,
    VoteMultipleChoiceNotAllowedError,
    VoteNoOptionError,
    VoteOptionNotFoundError,
    VotePollNotFoundError,
)
from src.models.poll import Poll
from src.models.poll_group import PollGroup
from src.models.poll_option import PollOption
from src.models.vote import Vote


def VoteProcess(db, vote_qr: str, normalized_annonymou_id: str, poll_id: str, options: list[int]):
    if db is None:
        raise Exception("DB 세션이 유효하지 않습니다.")
    if len(options) == 0:
        raise VoteNoOptionError()

    try:
        poll_uuid = uuid.UUID(str(poll_id))
    except (TypeError, ValueError) as exc:
        raise VoteInvalidPollIdError() from exc

    poll = (
        db.query(Poll)
        .join(PollGroup, Poll.group_id == PollGroup.id)
        .filter(Poll.id == poll_uuid, PollGroup.qr_token == vote_qr)
        .first()
    )
    if poll is None:
        raise VotePollNotFoundError()

    if not poll.allow_multiple_choice and len(options) > 1:
        raise VoteMultipleChoiceNotAllowedError()

    if db.query(Vote).filter(Vote.poll_id == poll_uuid, Vote.anonymous_id == normalized_annonymou_id).first():
        raise VoteAlreadyCastError()

    for option in options:
        poll_option = (
            db.query(PollOption)
            .filter(
                PollOption.id == option,
                PollOption.poll_id == poll_uuid,
                PollOption.poll_group_qr == vote_qr,
            )
            .first()
        )
        if poll_option is None:
            raise VoteOptionNotFoundError()

        vote = Vote(
            poll_id=poll.id,
            option_id=poll_option.id,
            anonymous_id=normalized_annonymou_id
        )
        db.add(vote)