from collections.abc import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import PollOption, Vote


def GetOptionsByPollID(db: Session, poll_id):
	return db.query(PollOption).filter(PollOption.poll_id == poll_id).all()


def HasAnonymousVoteForOptionIDs(
	db: Session,
	poll_id,
	anonymous_id,
	option_ids: Sequence[int],
) -> bool:
	if not option_ids:
		return False

	return (
		db.query(Vote)
		.filter(Vote.poll_id == poll_id)
		.filter(Vote.anonymous_id == anonymous_id)
		.filter(Vote.option_id.in_(option_ids))
		.first()
		is not None
	)


def CreateVotes(
	db: Session,
	poll_id,
	anonymous_id,
	option_ids: Sequence[int],
) -> None:
	current_max_id = db.query(func.coalesce(func.max(Vote.id), 0)).scalar() or 0
	vote_instances = [
		Vote(
			id=current_max_id + index,
			poll_id=poll_id,
			option_id=option_id,
			anonymous_id=anonymous_id,
		)
		for index, option_id in enumerate(option_ids, start=1)
	]

	db.add_all(vote_instances)
	try:
		db.commit()
	except Exception:
		db.rollback()
		raise

def CalculateVoteCount(db: Session, poll_id):
	rows = (
		db.query(Vote.option_id, func.count(Vote.id))
		.filter(Vote.poll_id == poll_id)
		.group_by(Vote.option_id)
		.all()
	)
	return {option_id: count for option_id, count in rows}



