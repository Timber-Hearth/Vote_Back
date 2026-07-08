import uuid
from datetime import UTC, datetime

from src.exceptions.vote import (
    VoteAlreadyCastError,
    VoteClosedError,
    VoteExpiredError,
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


def VoteProcess(db, vote_qr: str, normalized_annonymou_id: uuid.UUID, poll_id: str, options: list[int]):
    if db is None:
        raise Exception("DB 세션이 유효하지 않습니다.")
    if len(options) == 0:
        raise VoteNoOptionError()

    try:
        poll_uuid = uuid.UUID(str(poll_id))
    except (TypeError, ValueError) as exc:
        raise VoteInvalidPollIdError() from exc

    try:
        anonymous_uuid = uuid.UUID(str(normalized_annonymou_id))
    except (TypeError, ValueError) as exc:
        raise Exception("anonymous_id가 유효한 UUID가 아닙니다.") from exc

    poll_record = (
        db.query(Poll, PollGroup)
        .join(PollGroup, Poll.group_id == PollGroup.id)
        .filter(Poll.id == poll_uuid, PollGroup.qr_token == vote_qr)
        .first()
    )
    if poll_record is None:
        raise VotePollNotFoundError()

    poll, poll_group = poll_record

    if poll_group.is_closed:
        raise VoteClosedError()

    expire_at = poll_group.expire_at
    if expire_at is not None:
        if expire_at.tzinfo is None:
            expire_at = expire_at.replace(tzinfo=UTC)
        if expire_at <= datetime.now(UTC):
            raise VoteExpiredError()

    unique_option_ids = list(dict.fromkeys(options))

    if not poll.allow_multiple_choice and len(unique_option_ids) > 1:
        raise VoteMultipleChoiceNotAllowedError()

    if db.query(Vote).filter(Vote.poll_id == poll_uuid, Vote.anonymous_id == anonymous_uuid).first():
        raise VoteAlreadyCastError()

    valid_option_ids = {
        option_id
        for (option_id,) in (
            db.query(PollOption.id)
            .filter(
                PollOption.poll_id == poll_uuid,
                PollOption.poll_group_qr == vote_qr,
                PollOption.id.in_(unique_option_ids),
            )
            .all()
        )
    }

    if len(valid_option_ids) != len(unique_option_ids):
        raise VoteOptionNotFoundError()

    for option_id in unique_option_ids:
        db.add(
            Vote(
                poll_id=poll.id,
                option_id=option_id,
                anonymous_id=anonymous_uuid,
            )
        )

    db.flush()