from collections.abc import Sequence

from sqlalchemy.orm import Session

from src.models import PollOption, Polls
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